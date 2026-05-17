from fastapi import APIRouter, Depends
from schemas.request import ChatRequest
from schemas.response import ChatResponse
from agents.orchestrator import Orchestrator
from gateway.auth import verify_key

router = APIRouter()
orchestrator = Orchestrator()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, _=Depends(verify_key)):
    answer = await orchestrator.run(req.session_id, req.message)
    return ChatResponse(reply=answer)
