from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.chat_models import ChatRequest, ChatResponse
from services.ai_service import AIService
import logging

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

    Accepts arbitrary JSON, validates with Pydantic, and returns 422 on bad input
    instead of raising a 500 error.
    """
    try:
        # Read raw JSON and validate explicitly to provide clean 422 on errors
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # Ensure required field `message` exists before validation for clearer error
        if not isinstance(body, dict) or "message" not in body or not str(body.get("message", "")).strip():
            raise HTTPException(status_code=422, detail="Field 'message' is required")

        chat_req = ChatRequest.model_validate(body)

        logger.info(f"Chat request received: {chat_req.message[:50]}...")

        # Generate response using AI service
        response = await ai_service.generate_response(
            user_input=chat_req.message,
            history=chat_req.conversation_history
        )

        logger.info(
            "Response generated: format=%s, success=%s",
            response.get('format_type'), response.get('success')
        )

        return ChatResponse(**response)

    except HTTPException:
        # Re-raise expected HTTP errors (422/400)
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
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
