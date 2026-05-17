from tools.ticket_client import create_support_ticket

class EscalationAgent:
    async def handle(self, params: dict) -> str:
        return create_support_ticket(params["session_id"], params["reason"])
