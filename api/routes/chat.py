from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.chat_models import ChatRequest, ChatResponse, Message as ChatMsgModel
from services.ai_service import AIService
import logging
from typing import List, Dict, Any

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

    Accepts flexible payloads. Preferred shape:
    {
      "message": "...",
      "conversation_history": [{"username":"User","content":"...","timestamp":"..."}]
    }

    Also tolerates:
      - { "prompt": "..." }
      - { "text": "..." }
      - { "messages": [{"role":"user","content":"..."}, ...] }
    """
    try:
        try:
            body: Dict[str, Any] = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # Infer message from alternate fields if missing
        message: str = (body.get("message") or body.get("prompt") or body.get("text") or "").strip()

        # If still missing, try to derive from OpenAI-like messages array
        if not message and isinstance(body.get("messages"), list):
            for m in reversed(body["messages"]):
                if isinstance(m, dict) and m.get("role") == "user" and str(m.get("content", "")).strip():
                    message = str(m.get("content")).strip()
                    break

        # Build conversation history from either provided conversation_history or messages
        conv_history: List[Dict[str, Any]] = []
        if isinstance(body.get("conversation_history"), list):
            conv_history = body["conversation_history"]
        elif isinstance(body.get("messages"), list):
            # Map OpenAI-like messages to backend shape
            for m in body["messages"]:
                if not isinstance(m, dict) or "content" not in m:
                    continue
                role = m.get("role", "assistant")
                conv_history.append({
                    "username": "User" if role == "user" else "Assistant",
                    "content": m.get("content", ""),
                    "timestamp": m.get("timestamp") or m.get("time") or None
                })

        # Validate required message
        if not message:
            logger.warning("/api/v1/chat missing 'message'. Body keys: %s", list(body.keys()))
            raise HTTPException(status_code=422, detail="Field 'message' is required")

        # Compose normalized payload for model validation
        normalized: Dict[str, Any] = {
            "message": message,
            "conversation_history": conv_history,
            "user_id": body.get("user_id"),
            "room_id": body.get("room_id"),
        }

        chat_req = ChatRequest.model_validate(normalized)

        logger.info("Chat request received: %s...", chat_req.message[:80])

        # Generate response using AI service
        response = await ai_service.generate_response(
            user_input=chat_req.message,
            history=chat_req.conversation_history
        )

        return ChatResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.get("/chat/health")
async def chat_health_check():
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
