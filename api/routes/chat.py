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
    Supports conversation_id for maintaining conversation history.
    """
    try:
        try:
            body: Dict[str, Any] = await request.json()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON body")

        # ?? DEBUG: Log the entire body
        logger.info("=" * 60)
        logger.info("[DEBUG] CHAT ENDPOINT - REQUEST RECEIVED")
        logger.info(f"[DEBUG] Full request body keys: {list(body.keys())}")
        logger.info(f"[DEBUG] conversation_id in body: {body.get('conversation_id')}")
        logger.info(f"[DEBUG] Full body: {body}")
        logger.info("=" * 60)

        # Extract conversation_id if provided
        conversation_id = body.get("conversation_id")
        
        # ?? DEBUG: Log conversation_id extraction
        logger.info(f"[DEBUG] Extracted conversation_id: {conversation_id}")
        logger.info(f"[DEBUG] conversation_id type: {type(conversation_id)}")

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
            "conversation_id": conversation_id,
        }

        # ?? DEBUG: Log normalized payload
        logger.info("=" * 60)
        logger.info("[DEBUG] NORMALIZED PAYLOAD")
        logger.info(f"[DEBUG] normalized_payload conversation_id: {normalized_payload.get('conversation_id')}")
        logger.info(f"[DEBUG] normalized_payload keys: {list(normalized_payload.keys())}")
        logger.info("=" * 60)

        chat_req = ChatRequest.model_validate(normalized_payload)
        
        # ?? DEBUG: Log ChatRequest model
        logger.info("=" * 60)
        logger.info("[DEBUG] CHAT REQUEST MODEL")
        logger.info(f"[DEBUG] chat_req.conversation_id: {chat_req.conversation_id}")
        logger.info(f"[DEBUG] chat_req.message: {chat_req.message[:80]}...")
        logger.info(f"[DEBUG] chat_req.user_id: {chat_req.user_id}")
        logger.info(f"[DEBUG] chat_req.room_id: {chat_req.room_id}")
        logger.info("=" * 60)
        
        logger.info("Chat request received: %s... (conversation_id: %s)", 
                   chat_req.message[:80], 
                   chat_req.conversation_id)

        # ?? DEBUG: Before calling AI service
        logger.info("=" * 60)
        logger.info("[DEBUG] CALLING AI SERVICE")
        logger.info(f"[DEBUG] Passing conversation_id to AI service: {chat_req.conversation_id}")
        logger.info("=" * 60)

        # Pass conversation_id to AI service
        response = await ai_service.generate_response(
            user_input=chat_req.message,
            history=chat_req.conversation_history,
            conversation_id=chat_req.conversation_id
        )
        
        # ?? DEBUG: Log response
        logger.info("=" * 60)
        logger.info("[DEBUG] AI SERVICE RESPONSE")
        logger.info(f"[DEBUG] Response conversation_id: {response.get('conversation_id')}")
        logger.info(f"[DEBUG] Response conversation_length: {response.get('conversation_length')}")
        logger.info(f"[DEBUG] Response success: {response.get('success')}")
        logger.info("=" * 60)
        
        # Log conversation info
        if chat_req.conversation_id:
            logger.info("Response generated for conversation %s (length: %d)", 
                       chat_req.conversation_id,
                       response.get('conversation_length', 0))
        
        chat_response = ChatResponse(**response)
        
        # ?? DEBUG: Log final response
        logger.info("=" * 60)
        logger.info("[DEBUG] FINAL RESPONSE")
        logger.info(f"[DEBUG] ChatResponse.conversation_id: {chat_response.conversation_id}")
        logger.info(f"[DEBUG] ChatResponse.conversation_length: {chat_response.conversation_length}")
        logger.info("=" * 60)
        
        return chat_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")


@router.get("/chat/health")
async def chat_health_check():
    try:
        ai_service = get_ai_service()
        claude_client = ai_service.claude_client
        
        # Get active conversation count
        active_conversations = 0
        if claude_client.is_enabled:
            model_info = claude_client.get_model_info()
            active_conversations = model_info.get("active_conversations", 0)
        
        return {
            "status": "healthy",
            "claude_enabled": claude_client.is_enabled,
            "active_conversations": active_conversations,
            "services": {
                "context_analyzer": "ready",
                "format_selector": "ready",
                "response_formatter": "ready"
            },
            "features": [
                "context_aware_responses",
                "markdown_formatting",
                "conversation_history"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# Conversation management endpoints
@router.post("/chat/conversation/clear")
async def clear_chat_conversation(
    conversation_id: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Clear conversation history for a specific conversation ID.
    
    Example:
        POST /api/v1/chat/conversation/clear?conversation_id=user_123
    """
    try:
        if not ai_service.claude_client.is_enabled:
            raise HTTPException(status_code=503, detail="AI features not configured")
        
        ai_service.claude_client.clear_conversation(conversation_id)
        return {
            "success": True,
            "message": f"Conversation history cleared for: {conversation_id}"
        }
    except Exception as e:
        logger.error(f"Failed to clear conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/conversation/{conversation_id}/history")
async def get_chat_conversation_history(
    conversation_id: str,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Get conversation history for a specific conversation ID.
    
    Example:
        GET /api/v1/chat/conversation/user_123/history
    """
    try:
        if not ai_service.claude_client.is_enabled:
            raise HTTPException(status_code=503, detail="AI features not configured")
        
        history = ai_service.claude_client.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "message_count": len(history)
        }
    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
