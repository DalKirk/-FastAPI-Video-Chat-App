from fastapi import APIRouter, HTTPException, Depends, Request
from app.models.chat_models import ChatRequest, ChatResponse
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
    Accept flexible payloads and normalize to ChatRequest.
    Derive message from message/prompt/text, messages[], or conversation_history[].
    Normalize conversation_history entries to {username, content, timestamp}.
    """
    try:
        try:
            body: Dict[str, Any] = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # 1) Derive message from preferred fields
        message: str = (body.get("message") or body.get("prompt") or body.get("text") or "").strip()

        # 2) Derive from messages[] if needed
        if not message and isinstance(body.get("messages"), list):
            for m in reversed(body["messages"]):
                if not isinstance(m, dict):
                    continue
                content = (str(m.get("content") or m.get("message") or m.get("text") or "")).strip()
                role = (m.get("role") or "").strip().lower()
                if role == "user" and content:
                    message = content
                    break
            # fallback: last non-empty content
            if not message:
                for m in reversed(body["messages"]):
                    if not isinstance(m, dict):
                        continue
                    content = (str(m.get("content") or m.get("message") or m.get("text") or "")).strip()
                    if content:
                        message = content
                        break

        # Prepare conversation history (normalize entries)
        raw_history = body.get("conversation_history")
        normalized_history: List[Dict[str, Any]] = []

        if isinstance(raw_history, list):
            for item in raw_history:
                if not isinstance(item, dict):
                    continue
                # map possible keys to expected ones
                role = (item.get("role") or "").strip().lower()
                username = item.get("username")
                if not username:
                    username = "User" if role == "user" else ("Assistant" if role else "Assistant")
                content = (str(item.get("content") or item.get("message") or item.get("text") or "")).strip()
                ts = item.get("timestamp") or item.get("time") or None

                normalized_history.append({
                    "username": username,
                    "content": content,
                    "timestamp": ts
                })

            # 3) Derive message from conversation_history if still missing
            if not message:
                # prefer last user entry with non-empty content
                for m in reversed(normalized_history):
                    if m.get("username", "").strip().lower() == "user" and m.get("content"):
                        message = m["content"].strip()
                        break
                # fallback: any last non-empty content
                if not message:
                    for m in reversed(normalized_history):
                        if m.get("content"):
                            message = m["content"].strip()
                            break

        # Also map messages[] to history if history not provided
        if not normalized_history and isinstance(body.get("messages"), list):
            for m in body["messages"]:
                if not isinstance(m, dict):
                    continue
                role = (m.get("role") or "").strip().lower()
                username = "User" if role == "user" else "Assistant"
                content = (str(m.get("content") or m.get("message") or m.get("text") or "")).strip()
                ts = m.get("timestamp") or m.get("time") or None
                normalized_history.append({
                    "username": username,
                    "content": content,
                    "timestamp": ts
                })

        if not message:
            logger.warning("/api/v1/chat missing 'message'. Body keys: %s", list(body.keys()))
            raise HTTPException(status_code=422, detail="Field 'message' is required")

        normalized_payload: Dict[str, Any] = {
            "message": message,
            "conversation_history": normalized_history,
            "user_id": body.get("user_id"),
            "room_id": body.get("room_id"),
        }

        chat_req = ChatRequest.model_validate(normalized_payload)
        logger.info("Chat request received: %s...", chat_req.message[:80])

        response = await ai_service.generate_response(
            user_input=chat_req.message,
            history=chat_req.conversation_history
        )
        return ChatResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


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
        return {"status": "unhealthy", "error": str(e)}
