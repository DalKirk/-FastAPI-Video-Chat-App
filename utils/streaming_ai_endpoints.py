"""
Streaming AI endpoint for Claude API with Server-Sent Events (SSE)
Add this to your main.py or import the streaming_ai_router
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from utils.claude_client import get_claude_client
import json
import anthropic
import logging

logger = logging.getLogger(__name__)

# Create router for streaming AI endpoints
streaming_ai_router = APIRouter(prefix="/ai/stream", tags=["AI Streaming"])


class StreamChatRequest(BaseModel):
    """Request for streaming chat"""
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "..."}, ...]
    max_tokens: int = 2048
    temperature: float = 0.7
    system: Optional[str] = None
    conversation_id: Optional[str] = None  # Conversation tracking


class StreamGenerateRequest(BaseModel):
    """Request for streaming generation"""
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    conversation_id: Optional[str] = None  # Conversation tracking


# Streaming Chat Endpoint (Multi-turn conversations)
@streaming_ai_router.post("/chat")
async def stream_chat(request: StreamChatRequest):
    """
    Stream Claude chat responses using Server-Sent Events (SSE).
    Claude's markdown output is passed through directly without modification.
    """
    claude = get_claude_client()

    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    # Log incoming request
    logger.info(f"?? Stream chat request (conversation_id={request.conversation_id}, messages={len(request.messages)})")

    async def generate():
        try:
            # ? Get or create conversation history
            if request.conversation_id:
                if request.conversation_id not in claude.conversations:
                    claude.conversations[request.conversation_id] = []
                # Get existing conversation history
                conversation_messages = claude.conversations[request.conversation_id].copy()
                # Append new messages from request
                conversation_messages.extend(request.messages)
            else:
                # No conversation tracking - just use request messages
                conversation_messages = request.messages
            
            logger.info(f"?? Using {len(conversation_messages)} messages in conversation history")
            
            # Build system prompt with date context
            date_context = claude._get_current_date_context()
            system_prompt = request.system or ""
            
            if system_prompt:
                system_prompt = f"{date_context}\n\n{system_prompt}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."

            # Stream Claude's response with full conversation history
            logger.info(f"?? Starting stream with model: {claude.active_model}")
            
            full_response = ""  # ? Track full response for saving to history
            
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=conversation_messages,  # ? Use full conversation history
            ) as stream:
                chunk_count = 0
                for text in stream.text_stream:
                    chunk = text or ""
                    chunk_count += 1
                    full_response += chunk  # ? Accumulate response
                    yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                
                logger.info(f"? Stream completed ({chunk_count} chunks)")
            
            # ? Save conversation history
            if request.conversation_id:
                # Save the new messages to conversation history
                for msg in request.messages:
                    if msg not in claude.conversations[request.conversation_id]:
                        claude.conversations[request.conversation_id].append(msg)
                # Save assistant's response
                claude.conversations[request.conversation_id].append({
                    "role": "assistant",
                    "content": full_response
                })
                logger.info(f"?? Saved to conversation {request.conversation_id} (total: {len(claude.conversations[request.conversation_id])} messages)")

            # Send completion with metadata
            completion_data = {
                'type': 'done', 
                'model': claude.active_model,
                'conversation_id': request.conversation_id,
                'conversation_length': len(claude.conversations.get(request.conversation_id, []))
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except anthropic.NotFoundError as e:
            logger.error(f"? Model not found: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': f'Model not found: {str(e)}'})}\n\n"
        except anthropic.AuthenticationError as e:
            logger.error(f"? Authentication error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            logger.error(f"? Streaming error: {e}", exc_info=True)
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
    Claude's markdown output is passed through directly without modification.
    """
    claude = get_claude_client()

    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    logger.info(f"?? Stream generate request (prompt_length={len(request.prompt)})")

    async def generate():
        try:
            # Build system prompt with date context
            date_context = claude._get_current_date_context()
            if request.system_prompt:
                system_prompt = f"{date_context}\n\n{request.system_prompt}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."

            messages = [{"role": "user", "content": request.prompt}]

            # Stream Claude's response directly without modification
            logger.info(f"?? Starting stream with model: {claude.active_model}")
            
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=messages,
            ) as stream:
                chunk_count = 0
                for text in stream.text_stream:
                    chunk = text or ""
                    chunk_count += 1
                    yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                
                logger.info(f"? Stream completed ({chunk_count} chunks)")

            # Send completion with metadata
            completion_data = {
                'type': 'done', 
                'model': claude.active_model,
                'conversation_id': request.conversation_id
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except anthropic.NotFoundError:
            # Fallback to backup model
            logger.warning(f"?? Model not found, trying fallback")
            try:
                claude.active_model = claude.get_model_info()["fallback_model"]
                logger.info(f"?? Switched to fallback model: {claude.active_model}")
                
                with claude.client.messages.stream(
                    model=claude.active_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system=system_prompt,
                    messages=messages,
                ) as stream:
                    chunk_count = 0
                    for text in stream.text_stream:
                        chunk = text or ""
                        chunk_count += 1
                        yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                    
                    logger.info(f"? Fallback stream completed ({chunk_count} chunks)")
                
                # Send fallback completion
                fallback_data = {
                    'type': 'done', 
                    'model': claude.active_model, 
                    'fallback': True
                }
                yield f"data: {json.dumps(fallback_data)}\n\n"
            except Exception as fallback_error:
                logger.error(f"? Fallback also failed: {fallback_error}")
                yield f"data: {json.dumps({'type': 'error', 'error': f'Both models failed: {str(fallback_error)}'})}\n\n"
        except anthropic.AuthenticationError:
            logger.error(f"? Authentication error")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            logger.error(f"? Streaming error: {e}", exc_info=True)
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
        "text_formatting": "raw Claude output (unmodified)",
        "features": {
            "conversation_history": True,
            "markdown": True
        }
    }


# To use these endpoints in your main.py, add:
# from utils.streaming_ai_endpoints import streaming_ai_router
# app.include_router(streaming_ai_router)
