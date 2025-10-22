"""
Streaming AI endpoint for Claude API with Server-Sent Events (SSE)
Add this to your main.py or import the streaming_ai_router
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
from utils.claude_client import get_claude_client, format_text
import json
import anthropic
import logging

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


def _needs_leading_space(prev_last: Optional[str], nxt: str, in_code: bool) -> bool:
    """Decide whether to insert a space at chunk boundary.
    Insert when previous non-space char is sentence/phrase punctuation and the
    current chunk begins with a letter/number and not already a space.
    Never insert inside code blocks or before a code fence.
    """
    if in_code or not prev_last or not nxt:
        return False
    first = nxt[0]
    if first.isspace() or first == '`':
        return False
    boundary_punct = ".!?,:;)\]"  # punctuation that should be followed by space
    if prev_last in boundary_punct and (first.isalnum() or first in '"\'('):
        return True
    return False


def _last_non_space(text: str) -> Optional[str]:
    for ch in reversed(text):
        if not ch.isspace():
            return ch
    return None


def _process_chunk_with_code_fences(chunk: str, in_code: bool, prev_last: Optional[str]) -> Tuple[str, bool, Optional[str]]:
    """Split chunk on triple backticks and only format non-code segments.
    Returns (emitted_text, new_in_code_state, new_prev_last_char)
    """
    if not chunk:
        return chunk, in_code, prev_last

    # Optionally insert a space at the very front if needed (and not in code)
    if _needs_leading_space(prev_last, chunk, in_code):
        chunk = " " + chunk

    # Fast path: no fences in this chunk
    if "```" not in chunk:
        if in_code:
            emitted = chunk
        else:
            emitted = format_text(chunk)
        return emitted, in_code, _last_non_space(emitted) or prev_last

    parts = chunk.split("```")
    emitted_parts: List[str] = []
    current_in_code = in_code

    for i, part in enumerate(parts):
        if i == 0:
            # Leading segment before first fence
            if current_in_code:
                emitted_parts.append(part)
            else:
                emitted_parts.append(format_text(part))
        else:
            # Re-insert the fence
            emitted_parts.append("```")
            # Toggle code state after each fence
            current_in_code = not current_in_code
            # Append the content following the fence without modification if in code
            if current_in_code:
                emitted_parts.append(part)
            else:
                emitted_parts.append(format_text(part))

    emitted_text = "".join(emitted_parts)
    return emitted_text, current_in_code, _last_non_space(emitted_text) or prev_last


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
    
    Returns: Server-Sent Events stream with formatted text
    """
    claude = get_claude_client()
    
    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )
    
    async def generate():
        """Generate streaming response with formatting and boundary fixes"""
        try:
            # Add date context if system prompt provided. Also, guide code formatting.
            system_prompt = request.system or ""
            guidance = (
                "When including code, wrap it in triple backticks with a language identifier"
                " (e.g., ```python) and preserve whitespace/newlines exactly."
            )
            if system_prompt:
                date_context = claude._get_current_date_context()
                system_prompt = f"{date_context}\n\n{system_prompt}\n\n{guidance}"
            else:
                date_context = claude._get_current_date_context()
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant. {guidance}"
            
            prev_last = None  # track last non-space character emitted
            in_code = False   # track if inside a code block

            # Stream from Claude API
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=request.messages
            ) as stream:
                for text in stream.text_stream:
                    chunk = text or ""
                    emitted, in_code, prev_last = _process_chunk_with_code_fences(chunk, in_code, prev_last)
                    yield f"data: {json.dumps({'text': emitted, 'type': 'content'})}\n\n"
            
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
    Stream Claude AI generation using Server-Sent Events (SSE) with text formatting.
    
    Example:
        POST /ai/stream/generate
        {
            "prompt": "Write a short story about a robot",
            "max_tokens": 1000,
            "temperature": 0.8
        }
    
    Returns: Server-Sent Events stream with formatted text
    """
    claude = get_claude_client()
    
    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )
    
    async def generate():
        """Generate streaming response with formatting and boundary fixes"""
        try:
            # Prepare system prompt with date context and code formatting guidance
            date_context = claude._get_current_date_context()
            guidance = (
                "When including code, wrap it in triple backticks with a language identifier"
                " (e.g., ```python) and preserve whitespace/newlines exactly."
            )
            if request.system_prompt:
                system_prompt = f"{date_context}\n\n{request.system_prompt}\n\n{guidance}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant. {guidance}"
            
            # Convert prompt to messages format
            messages = [{"role": "user", "content": request.prompt}]

            prev_last = None  # track last non-space character emitted
            in_code = False   # track if inside a code block
            
            # Stream from Claude API
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=messages
            ) as stream:
                for text in stream.text_stream:
                    chunk = text or ""
                    emitted, in_code, prev_last = _process_chunk_with_code_fences(chunk, in_code, prev_last)
                    yield f"data: {json.dumps({'text': emitted, 'type': 'content'})}\n\n"
            
            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'model': claude.active_model})}\n\n"
            
        except anthropic.NotFoundError as e:
            # Try fallback model
            try:
                claude.active_model = claude.get_model_info()["fallback_model"]
                prev_last = None
                in_code = False
                with claude.client.messages.stream(
                    model=claude.active_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system=system_prompt,
                    messages=messages
                ) as stream:
                    for text in stream.text_stream:
                        chunk = text or ""
                        emitted, in_code, prev_last = _process_chunk_with_code_fences(chunk, in_code, prev_last)
                        yield f"data: {json.dumps({'text': emitted, 'type': 'content'})}\n\n"
                
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
        "format": "Server-Sent Events (SSE)",
        "text_formatting": "enabled"
    }


# To use these endpoints in your main.py, add:
# from utils.streaming_ai_endpoints import streaming_ai_router
# app.include_router(streaming_ai_router)
