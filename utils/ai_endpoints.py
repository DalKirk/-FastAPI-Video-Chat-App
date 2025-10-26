"""
Example AI endpoints using Claude API
Add these to your main.py to enable AI features
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from utils.claude_client import get_claude_client
import logging
import json

logger = logging.getLogger(__name__)

# Create router for AI endpoints
ai_router = APIRouter(prefix="/ai", tags=["AI Features"])


class ContentModerationRequest(BaseModel):
    """Request for content moderation"""
    content: str


class ConversationSummaryRequest(BaseModel):
    """Request for conversation summary"""
    messages: List[dict]  # [{"username": str, "content": str}, ...]


class SmartReplyRequest(BaseModel):
    """Request for smart reply suggestion"""
    context: str
    user_message: str


# AI Generation Endpoint - tolerant parser
@ai_router.post("/generate")
async def generate_ai_response(request: Request):
    """
    Generate AI response using Claude.

    Accepts payloads:
    - {"prompt": "..."
    - {"message"|"input"|"query"|"text": "..."
    - JSON string body: "....
    - Raw text/plain body: ...

    Optional fields: {"max_tokens": int, "temperature": float}
    """
    claude = get_claude_client()

    if not claude.is_enabled:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    # Defaults
    prompt: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7

    # Try JSON first
    body_bytes = await request.body()
    raw_text = (body_bytes or b"").decode("utf-8", errors="ignore").strip()

    data: Any = None
    if raw_text:
        # If it's JSON, parse it; else treat as plain text
        try:
            data = json.loads(raw_text)
        except json.JSONDecodeError:
            data = raw_text

    # Coerce into prompt and optional params
    if isinstance(data, dict):
        prompt = (
            data.get("prompt")
            or data.get("message")
            or data.get("input")
            or data.get("query")
            or data.get("text")
        )
        # Optional overrides
        if isinstance(data.get("max_tokens"), int):
            max_tokens = int(data["max_tokens"])
        if isinstance(data.get("temperature"), (int, float)):
            temperature = float(data["temperature"])
    elif isinstance(data, str):
        prompt = data

    if not prompt or not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(status_code=422, detail="Missing prompt. Provide 'prompt' or 'message' (string body allowed).")

    try:
        response = claude.generate_response(
            prompt=prompt.strip(),
            max_tokens=max_tokens,
            temperature=temperature
        )
        model_info = claude.get_model_info()

        logger.info('=== BEFORE SENDING TO FRONTEND ===')
        logger.info(f'Response length: {len(response)}')
        logger.info(f'Has spaces: {" " in response}')
        logger.info(f'Space count: {response.count(" ")}')
        logger.info(f'First 200 chars: {response[:200]}')
        logger.info('================================')

        return {
            "response": response,
            "model": model_info["active_model"],
            "debug_info": {
                "response_length": len(response),
                "has_spaces": " " in response,
                "space_count": response.count(" "),
                "word_count": len(response.split())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# Content Moderation Endpoint
@ai_router.post("/moderate")
async def moderate_content(request: ContentModerationRequest):
    """
    Moderate content for safety.
    """
    claude = get_claude_client()

    if not claude.is_enabled:
        # Fail open if moderation is disabled
        return {
            "is_safe": True,
            "reason": "Moderation disabled",
            "confidence": 0.0
        }

    try:
        result = claude.moderate_content(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Moderation failed: {str(e)}")


# Spam Detection Endpoint
@ai_router.post("/detect-spam")
async def detect_spam(request: ContentModerationRequest):
    """
    Detect if message is spam.
    """
    claude = get_claude_client()

    if not claude.is_enabled:
        return {"is_spam": False, "confidence": 0.0}

    try:
        is_spam = claude.detect_spam(request.content)
        return {"is_spam": is_spam}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spam detection failed: {str(e)}")


# Conversation Summary Endpoint
@ai_router.post("/summarize")
async def summarize_conversation(request: ConversationSummaryRequest):
    """
    Summarize a conversation.
    """
    claude = get_claude_client()

    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI features not configured")

    try:
        summary = claude.summarize_conversation(request.messages)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


# Smart Reply Endpoint
@ai_router.post("/suggest-reply")
async def suggest_smart_reply(request: SmartReplyRequest):
    """
    Suggest a smart reply based on context.
    """
    claude = get_claude_client()

    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI features not configured")

    try:
        suggestion = claude.suggest_reply(request.context, request.user_message)
        return {"suggested_reply": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reply suggestion failed: {str(e)}")


# Health check for AI features
@ai_router.get("/health")
async def ai_health_check():
    """Check if AI features are available"""
    claude = get_claude_client()
    model_info = claude.get_model_info() if claude.is_enabled else {}

    return {
        "ai_enabled": claude.is_enabled,
        "model": model_info.get("active_model") if claude.is_enabled else None,
        "fallback_model": model_info.get("fallback_model") if claude.is_enabled else None,
        "features": [
            "content_moderation",
            "spam_detection",
            "conversation_summary",
            "smart_replies",
            "ai_generation"
        ] if claude.is_enabled else []
    }


# To use these endpoints in your main.py, add:
# from utils.ai_endpoints import ai_router
# app.include_router(ai_router)
