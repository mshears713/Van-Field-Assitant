from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..agent_service import AGENT_METADATA, get_agents, run_agent_chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    model: Optional[str] = None


@router.get("/agents")
async def list_agents() -> dict:
    return {"agents": get_agents()}


@router.post("/agents/{agent_id}/chat")
async def agent_chat(agent_id: str, request: ChatRequest) -> dict:
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail={"error": "Message cannot be empty.", "error_type": "empty_message"})

    result = await run_agent_chat(agent_id, request.message, request.context, request.model)

    if not result.get("ok") and result.get("error_type") == "invalid_agent":
        raise HTTPException(status_code=404, detail=result)

    return result
