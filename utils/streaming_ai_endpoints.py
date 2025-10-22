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


# Streaming Chat Endpoint (Multi-turn conversations)
@streaming_ai_router.post("/chat")
async def stream_chat(request: StreamChatRequest):
    """
    Stream Claude chat responses using Server-Sent Events (SSE).
    No punctuation or spacing modifications are applied; content is passed through as received.
    """
    claude = get_claude_client()

    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    async def generate():
        try:
            # Optional guidance to include language identifiers in code fences
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

            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=request.messages,
            ) as stream:
                for text in stream.text_stream:
                    chunk = text or ""
                    # Pass through without modification
                    yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"

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
            "X-Accel-Buffering": "no",  # Disable buffering for Nginx
        },
    )


# Streaming Generation Endpoint (Simple prompts)
@streaming_ai_router.post("/generate")
async def stream_generate(request: StreamGenerateRequest):
    """
    Stream Claude AI generation using Server-Sent Events (SSE).
    No punctuation or spacing modifications are applied; content is passed through as received.
    """
    claude = get_claude_client()

    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    async def generate():
        try:
            date_context = claude._get_current_date_context()
            guidance = (
                "When including code, wrap it in triple backticks with a language identifier"
                " (e.g., ```python) and preserve whitespace/newlines exactly."
            )
            if request.system_prompt:
                system_prompt = f"{date_context}\n\n{request.system_prompt}\n\n{guidance}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant. {guidance}"

            messages = [{"role": "user", "content": request.prompt}]

            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    chunk = text or ""
                    # Pass through without modification
                    yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"

            yield f"data: {json.dumps({'type': 'done', 'model': claude.active_model})}\n\n"

        except anthropic.NotFoundError:
            # Fallback to backup model
            try:
                claude.active_model = claude.get_model_info()["fallback_model"]
                with claude.client.messages.stream(
                    model=claude.active_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system=system_prompt,
                    messages=messages,
                ) as stream:
                    for text in stream.text_stream:
                        chunk = text or ""
                        yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                yield f"data: {json.dumps({'type': 'done', 'model': claude.active_model, 'fallback': True})}\n\n"
            except Exception as fallback_error:
                yield f"data: {json.dumps({'type': 'error', 'error': f'Both models failed: {str(fallback_error)}'})}\n\n"
        except anthropic.AuthenticationError:
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
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
        "text_formatting": "disabled (pass-through)",
    }


# To use these endpoints in your main.py, add:
# from utils.streaming_ai_endpoints import streaming_ai_router
# app.include_router(streaming_ai_router)
