"""
Streaming AI endpoint for Claude API with Server-Sent Events (SSE)
Add this to your main.py or import the streaming_ai_router
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from utils.claude_client import get_claude_client
import json
import anthropic

# Create router for streaming AI endpoints
streaming_ai_router = APIRouter(prefix="/ai/stream", tags=["AI Streaming"])


class StreamChatRequest(BaseModel):
    """Request for streaming chat"""
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "..."}, ...]
    max_tokens: int = 2048
    temperature: float = 0.7
    system: Optional[str] = None


class StreamGenerateRequest(BaseModel):
    """Request for streaming generation"""
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: Optional[str] = None


# Streaming Chat Endpoint (Multi-turn conversations)
@streaming_ai_router.post("/chat")
async def stream_chat(request: StreamChatRequest):
    """
    Stream Claude chat responses using Server-Sent Events (SSE).
    
    Example:
        POST /ai/stream/chat
        {
            "messages": [
                {"role": "user", "content": "Tell me a story"}
            ],
            "max_tokens": 2048,
            "temperature": 0.7
        }
    
    Returns: Server-Sent Events stream
    """
    claude = get_claude_client()
    
    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )
    
    async def generate():
        """Generate streaming response"""
        try:
            # Add date context if system prompt provided
            system_prompt = request.system
            if system_prompt:
                date_context = claude._get_current_date_context()
                system_prompt = f"{date_context}\n\n{system_prompt}"
            
            # Stream from Claude API
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=request.messages
            ) as stream:
                for text in stream.text_stream:
                    # Format as Server-Sent Event
                    yield f"data: {json.dumps({'text': text, 'type': 'content'})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'model': claude.active_model})}\n\n"
            
        except anthropic.NotFoundError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': f'Model not found: {str(e)}'})}\n\n"
        except anthropic.AuthenticationError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering for Nginx
        }
    )


# Streaming Generation Endpoint (Simple prompts)
@streaming_ai_router.post("/generate")
async def stream_generate(request: StreamGenerateRequest):
    """
    Stream Claude AI generation using Server-Sent Events (SSE).
    
    Example:
        POST /ai/stream/generate
        {
            "prompt": "Write a short story about a robot",
            "max_tokens": 1000,
            "temperature": 0.8
        }
    
    Returns: Server-Sent Events stream
    """
    claude = get_claude_client()
    
    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )
    
    async def generate():
        """Generate streaming response"""
        try:
            # Prepare system prompt with date context
            date_context = claude._get_current_date_context()
            if request.system_prompt:
                system_prompt = f"{date_context}\n\n{request.system_prompt}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."
            
            # Convert prompt to messages format
            messages = [{"role": "user", "content": request.prompt}]
            
            # Stream from Claude API
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    # Format as Server-Sent Event
                    yield f"data: {json.dumps({'text': text, 'type': 'content'})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'model': claude.active_model})}\n\n"
            
        except anthropic.NotFoundError as e:
            # Try fallback model
            try:
                claude.active_model = claude.get_model_info()["fallback_model"]
                
                with claude.client.messages.stream(
                    model=claude.active_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system=system_prompt,
                    messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        yield f"data: {json.dumps({'text': text, 'type': 'content'})}\n\n"
                
                yield f"data: {json.dumps({'type': 'done', 'model': claude.active_model, 'fallback': True})}\n\n"
                
            except Exception as fallback_error:
                yield f"data: {json.dumps({'type': 'error', 'error': f'Both models failed: {str(fallback_error)}'})}\n\n"
                
        except anthropic.AuthenticationError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# Health check for streaming endpoints
@streaming_ai_router.get("/health")
async def streaming_health_check():
    """Check if streaming AI features are available"""
    claude = get_claude_client()
    
    return {
        "streaming_enabled": claude.is_enabled,
        "model": claude.active_model if claude.is_enabled else None,
        "supports_streaming": True,
        "format": "Server-Sent Events (SSE)"
    }


# To use these endpoints in your main.py, add:
# from utils.streaming_ai_endpoints import streaming_ai_router
# app.include_router(streaming_ai_router)
