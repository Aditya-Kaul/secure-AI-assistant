"""POST /chat — main AI orchestration endpoint."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from backend.api.utils import rate_limit
from backend.services.ai_orchestrator import run_chat
from backend.db.history import save_query

log = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message:              str        = Field(..., min_length=1, max_length=1000)
    conversation_history: list[dict] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer:      str
    tool_calls:  list[dict]
    sources:     list[str]
    model:       str
    duration_ms: int


@router.post("/chat", response_model=ChatResponse, tags=["AI"])
async def chat(body: ChatRequest, _=Depends(rate_limit)):
    """
    Orchestrates AI + tools. Returns synthesized answer + full tool trace.
    """
    try:
        result = run_chat(
            user_message=body.message,
            conversation_history=body.conversation_history,
        )

        # Persist to history — don't fail the request if this errors
        try:
            save_query(
                question=body.message,
                answer=result["answer"],
                sources=result["sources"],
                tool_calls=result["tool_calls"],
                duration_ms=result["duration_ms"],
            )
        except Exception as he:
            log.warning("Failed to save to history: %s", he)

        return result

    except Exception as e:
        log.error("Chat error: %s", e)
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")