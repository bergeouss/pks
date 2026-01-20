from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import chat_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the knowledge base using RAG"""
    try:
        # Convert Pydantic models to dicts for service layer
        history = [h.model_dump() for h in request.history] if request.history else []

        response = await chat_service.chat(
            query=request.query,
            conversation_history=history,
        )
        return ChatResponse(**response)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
