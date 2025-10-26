from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.chat_models import ChatRequest, ChatResponse
from services.ai_service import AIService
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])

# Initialize AI service (singleton pattern)
_ai_service = None


def get_ai_service() -> AIService:
    """Dependency to get or create AIService instance."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: Request,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Main chat endpoint that provides context-aware, formatted AI responses.
    Accepts payloads shaped as ChatRequest or legacy/alternate shapes.
    """
    try:
        raw = await request.body()
        if not raw:
            raise HTTPException(status_code=400, detail="Empty request body")

        # Try JSON, else treat as raw text
        body: object
        try:
            body = json.loads(raw.decode("utf-8", errors="ignore"))
        except json.JSONDecodeError:
            # Plain text body -> treat as message
            body = {"message": raw.decode("utf-8", errors="ignore").strip()}

        chat_req = ChatRequest.model_validate(body)
        logger.info(f"Chat request received: {chat_req.message[:50]}...")

        # Generate response using AI service
        response = await ai_service.generate_response(
            user_input=chat_req.message,
            history=chat_req.conversation_history
        )

        logger.info(f"Response generated: format={response.get('format_type')}, success={response.get('success')}")

        return ChatResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        # If validation error surfaced, provide clear detail
        msg = str(e)
        status = 422 if "message' is required" in msg or "Empty request body" in msg else 500
        raise HTTPException(
            status_code=status,
            detail=f"Failed to generate response: {msg}"
        )


@router.get("/chat/health")
async def chat_health_check():
    """Health check endpoint for the chat service."""
    try:
        ai_service = get_ai_service()
        return {
            "status": "healthy",
            "claude_enabled": ai_service.claude_client.is_enabled,
            "services": {
                "context_analyzer": "ready",
                "format_selector": "ready",
                "response_formatter": "ready"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
