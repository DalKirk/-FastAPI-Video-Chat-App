"""
Example AI endpoints using Claude API
Add these to your main.py to enable AI features
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.claude_client import get_claude_client

# Create router for AI endpoints
ai_router = APIRouter(prefix="/ai", tags=["AI Features"])


class AIRequest(BaseModel):
    """Request for AI generation"""
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7


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


# AI Generation Endpoint
@ai_router.post("/generate")
async def generate_ai_response(request: AIRequest):
    """
    Generate AI response using Claude.
    
    Example:
        POST /ai/generate
        {
            "prompt": "Write a fun icebreaker for a chat room",
            "max_tokens": 100,
            "temperature": 0.8
        }
    """
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )
    
    try:
        response = claude.generate_response(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        return {"response": response, "model": "claude-3-5-sonnet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


# Content Moderation Endpoint
@ai_router.post("/moderate")
async def moderate_content(request: ContentModerationRequest):
    """
    Moderate content for safety.
    
    Example:
        POST /ai/moderate
        {
            "content": "This is a test message"
        }
    
    Returns:
        {
            "is_safe": true,
            "reason": "No violations detected",
            "confidence": 0.95
        }
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
    
    Returns:
        {
            "is_spam": true/false,
            "confidence": 0.0-1.0
        }
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
    
    Example:
        POST /ai/summarize
        {
            "messages": [
                {"username": "Alice", "content": "Hello!"},
                {"username": "Bob", "content": "Hi Alice!"},
                ...
            ]
        }
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
    
    Example:
        POST /ai/suggest-reply
        {
            "context": "Alice: How's everyone doing today?",
            "user_message": "I'm doing great! How about you?"
        }
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
    return {
        "ai_enabled": claude.is_enabled,
        "model": "claude-3-5-sonnet-20241022" if claude.is_enabled else None,
        "features": [
            "content_moderation",
            "spam_detection",
            "conversation_summary",
            "smart_replies",
            "ai_generation"
        ] if claude.is_enabled else []
    }


# To use these endpoints in your main.py, add:
# from ai_endpoints import ai_router
# app.include_router(ai_router)
