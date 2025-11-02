"""
Example AI endpoints using Claude API
Add these to your main.py to enable AI features
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from utils.claude_client import get_claude_client
import logging

logger = logging.getLogger(__name__)

# Create router for AI endpoints
ai_router = APIRouter(prefix="/ai", tags=["AI Features"])


class AIRequest(BaseModel):
    """Request for AI generation"""
    prompt: str
    max_tokens: int = 1000
    temperature: float = 0.7
    conversation_id: Optional[str] = None  # Optional conversation tracking
    enable_search: bool = True  # NEW: Enable/disable web search


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
    conversation_id: Optional[str] = None  # NEW: Optional conversation tracking


# NEW: Conversation management endpoints
class ConversationManagementRequest(BaseModel):
    """Request for conversation management"""
    conversation_id: str


# AI Generation Endpoint
@ai_router.post("/generate")
async def generate_ai_response(request: AIRequest):
    """
    Generate AI response using Claude with optional conversation history and web search.
    
    Example without history:
        POST /ai/generate
        {
            "prompt": "Write a fun icebreaker for a chat room",
            "max_tokens": 100,
            "temperature": 0.8
        }
    
    Example with conversation history:
        POST /ai/generate
        {
            "prompt": "What did I just tell you?",
            "max_tokens": 100,
            "temperature": 0.7,
            "conversation_id": "user_123"
        }
    
    Example with web search:
        POST /ai/generate
        {
            "prompt": "What's the latest news on AI?",
            "max_tokens": 200,
            "temperature": 0.7,
            "conversation_id": "user_123",
            "enable_search": true
        }
    """
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )
    
    try:
        response = await claude.generate_response(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            conversation_id=request.conversation_id,
            enable_search=request.enable_search  # NEW: Pass enable_search flag
        )
        model_info = claude.get_model_info()
        
        # Diagnostic logging
        logger.info('=== AI GENERATE RESPONSE ===')
        logger.info(f'Response length: {len(response)}')
        logger.info(f'Conversation ID: {request.conversation_id}')
        logger.info(f'Search enabled: {request.enable_search}')  # NEW: Log search status
        if request.conversation_id:
            logger.info(f'History length: {claude.get_conversation_count(request.conversation_id)}')
        logger.info('============================')
        
        return {
            "response": response, 
            "model": model_info["active_model"],
            "search_enabled": claude.is_search_enabled,  # NEW: Return search status
            "conversation_id": request.conversation_id,
            "conversation_length": claude.get_conversation_count(request.conversation_id) if request.conversation_id else 0,
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
    
    Note: Content moderation does NOT use conversation history (each check is independent)
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
        summary = await claude.summarize_conversation(request.messages)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


# Smart Reply Endpoint
@ai_router.post("/suggest-reply")
async def suggest_smart_reply(request: SmartReplyRequest):
    """
    Suggest a smart reply based on context, with optional conversation history.
    
    Example without history:
        POST /ai/suggest-reply
        {
            "context": "Alice: How's everyone doing today?",
            "user_message": "I'm doing great! How about you?"
        }
    
    Example with conversation history:
        POST /ai/suggest-reply
        {
            "context": "Alice: How's everyone doing today?",
            "user_message": "I'm doing great! How about you?",
            "conversation_id": "alice_123"
        }
    """
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI features not configured")
    
    try:
        suggestion = await claude.suggest_reply(request.context, request.user_message)
        
        return {
            "suggested_reply": suggestion,
            "conversation_id": request.conversation_id,
            "conversation_length": claude.get_conversation_count(request.conversation_id) if request.conversation_id else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reply suggestion failed: {str(e)}")


# NEW: Conversation Management Endpoints
@ai_router.post("/conversation/clear")
async def clear_conversation(request: ConversationManagementRequest):
    """
    Clear conversation history for a specific conversation ID.
    
    Example:
        POST /ai/conversation/clear
        {
            "conversation_id": "user_123"
        }
    """
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI features not configured")
    
    try:
        claude.clear_conversation(request.conversation_id)
        return {
            "success": True,
            "message": f"Conversation history cleared for: {request.conversation_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear conversation: {str(e)}")


@ai_router.get("/conversation/{conversation_id}/history")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history for a specific conversation ID.
    
    Example:
        GET /ai/conversation/user_123/history
    
    Returns:
        {
            "conversation_id": "user_123",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            "message_count": 2
        }
    """
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI features not configured")
    
    try:
        history = claude.get_conversation_history(conversation_id)
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "message_count": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation history: {str(e)}")


@ai_router.get("/conversation/{conversation_id}/count")
async def get_conversation_count(conversation_id: str):
    """
    Get message count for a specific conversation ID.
    
    Example:
        GET /ai/conversation/user_123/count
    
    Returns:
        {
            "conversation_id": "user_123",
            "message_count": 10
        }
    """
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI features not configured")
    
    try:
        count = claude.get_conversation_count(conversation_id)
        return {
            "conversation_id": conversation_id,
            "message_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation count: {str(e)}")


# Health check for AI features
@ai_router.get("/health")
async def ai_health_check():
    """Check if AI features are available"""
    claude = get_claude_client()
    model_info = claude.get_model_info() if claude.is_enabled else {}
    
    return {
        "ai_enabled": claude.is_enabled,
        "search_enabled": claude.is_search_enabled if claude.is_enabled else False,  # NEW: Search status
        "model": model_info.get("active_model") if claude.is_enabled else None,
        "fallback_model": model_info.get("fallback_model") if claude.is_enabled else None,
        "active_conversations": model_info.get("active_conversations", 0) if claude.is_enabled else 0,
        "features": [
            "content_moderation",
            "spam_detection",
            "conversation_summary",
            "smart_replies",
            "ai_generation",
            "conversation_history",
            "web_search"  # NEW: Web search feature
        ] if claude.is_enabled else []
    }


# To use these endpoints in your main.py, add:
# from utils.ai_endpoints import ai_router
# app.include_router(ai_router)
