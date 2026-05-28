import logging
import traceback
import asyncio
from google import genai
from google.genai import types
from config.settings import settings
from memory.session_store import SessionStore
from agents.faq_agent import FAQAgent
from agents.order_agent import OrderAgent
from agents.billing_agent import BillingAgent
from agents.escalation_agent import EscalationAgent
from agents.refund_agent import RefundAgent

# Set up clean logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Orchestrator")

# Define Tool Functions globally for Gemini inspection
def faq(query: str) -> str:
    """Answer product or policy FAQs using semantic search."""
    return ""

def order(order_id: str) -> str:
    """Look up details and status for a specific order ID."""
    return ""

def refund(order_id: str) -> str:
    """Check if an order is eligible for a refund or initiate a refund."""
    return ""

def billing(query: str) -> str:
    """Handle questions about invoices, payments, or subscriptions."""
    return ""

def escalate(reason: str) -> str:
    """Escalate to a human agent when the AI cannot resolve the issue."""
    return ""

class Orchestrator:
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.store = SessionStore()
        self.agents = {
            "faq": FAQAgent(),
            "order": OrderAgent(),
            "billing": BillingAgent(),
            "escalate": EscalationAgent(),
            "refund": RefundAgent()
        }
        self.tools = [faq, order, refund, billing, escalate]
        # PRIORITY LIST OF ALL AVAILABLE MODELS (2026 Edition)
        self.models = [
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-2.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-8b-latest"
        ]

    async def _call_gemini_with_fallback(self, contents, config, current_model_idx=0):
        """Try calling Gemini models in order until one succeeds."""
        for i in range(current_model_idx, len(self.models)):
            model_name = self.models[i]
            try:
                logger.info(f"Trying model: {model_name}")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config
                )
                return response, i # Return response and which model worked
            except Exception as e:
                err_msg = str(e).lower()
                if any(x in err_msg for x in ["429", "503", "404", "not found", "quota", "unavailable"]):
                    logger.warning(f"Model {model_name} failed ({err_msg[:50]})... switching to next.")
                    continue
                raise e
        raise Exception("All Gemini models are currently exhausted or unavailable.")

    async def run(self, session_id: str, message: str) -> str:
        logger.info(f"--- Processing: {message} ---")
        try:
            raw_history = self.store.get(session_id)
            if len(raw_history) > 6: raw_history = raw_history[-6:]
            
            contents = []
            for h in raw_history:
                # Skip any history entries with missing/None content (from previous failed turns)
                if not h.get("content"):
                    continue
                role = "user" if h["role"] == "user" else "model"
                contents.append(types.Content(role=role, parts=[types.Part(text=h["content"])]))

            user_content = contents + [types.Content(role="user", parts=[types.Part(text=message)])]
            
            config = types.GenerateContentConfig(
                tools=self.tools,
                automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                system_instruction=(
                    "You are a friendly and knowledgeable AI assistant. "
                    "You can answer general knowledge questions, have casual conversations, and help with any topic. "
                    "Additionally, you have specialized tools for customer support tasks — use them when the user asks about: "
                    "specific order status or tracking (use 'order' tool), "
                    "refund eligibility or requests (use 'refund' tool), "
                    "billing, invoices, or payment questions (use 'billing' tool), "
                    "product or policy FAQs (use 'faq' tool), "
                    "or when you cannot resolve an issue and need to escalate (use 'escalate' tool). "
                    "For everything else — general questions, greetings, advice, calculations, etc. — just answer directly without using any tools."
                )
            )

            # --- INITIAL GENERATION WITH FALLBACK ---
            response, model_idx = await self._call_gemini_with_fallback(user_content, config)

            candidates = response.candidates
            if not candidates or not isinstance(candidates, list) or len(candidates) == 0:
                return "The AI engine is currently resting. Please try again in a moment."

            content = candidates[0].content
            if not content or not hasattr(content, "parts") or not content.parts:
                return "The AI engine is currently resting. Please try again in a moment."

            parts = content.parts
            if not isinstance(parts, list) or len(parts) == 0:
                return "The AI engine is currently resting. Please try again in a moment."

            part = parts[0]
            
            if part.function_call:
                fn = part.function_call
                agent_name = fn.name
                if not agent_name:
                    return "I'm sorry, I'm having a technical issue routing your request."

                args = dict(fn.args) if fn.args else {}
                logger.info(f"Tool Requested: {agent_name} (using {self.models[model_idx]})")
                
                if agent_name == "escalate": args["session_id"] = session_id
                
                agent = self.agents.get(agent_name)
                if agent:
                    result = await agent.handle(args)
                    
                    # --- FOLLOW-UP WITH FALLBACK ---
                    followup_content = user_content + [
                        content,
                        types.Content(role="user", parts=[types.Part.from_function_response(
                            name=agent_name, response={"result": result}
                        )])
                    ]
                    # Start from the same model that worked before to be efficient
                    final_response, _ = await self._call_gemini_with_fallback(followup_content, config, model_idx)
                    # .text returns None when response only has non-text parts (e.g. another function_call)
                    answer = final_response.text or "I've processed your request. Is there anything else I can help you with?"
                else:
                    answer = "I'm sorry, I'm having a technical issue routing your request."
            else:
                answer = response.text or "I'm sorry, I couldn't generate a response. Please try again."

            # Update history
            raw_history.append({"role": "user", "content": message})
            raw_history.append({"role": "assistant", "content": answer})
            self.store.set(session_id, raw_history)
            
            return answer

        except Exception as e:
            logger.error(f"FATAL: {str(e)}")
            return "All AI circuits are currently busy. Please try again in 60 seconds."
