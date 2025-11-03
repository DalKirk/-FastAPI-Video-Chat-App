"""
Streaming AI endpoint for Claude API with Server-Sent Events (SSE) and Web Search
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
    enable_search: bool = True  # Enable/disable web search
    conversation_id: Optional[str] = None  # Conversation tracking


class StreamGenerateRequest(BaseModel):
    """Request for streaming generation"""
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    enable_search: bool = True  # Enable/disable web search
    conversation_id: Optional[str] = None  # Conversation tracking


# Streaming Chat Endpoint (Multi-turn conversations)
@streaming_ai_router.post("/chat")
async def stream_chat(request: StreamChatRequest):
    """
    Stream Claude chat responses using Server-Sent Events (SSE) with optional web search.
    Claude's markdown output is passed through directly without modification.
    """
    claude = get_claude_client()

    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    # Log incoming request
    logger.info(f"??? Stream chat request (enable_search={request.enable_search}, "
                f"conversation_id={request.conversation_id}, messages={len(request.messages)})")

    async def generate():
        try:
            # Extract last user message for potential search query
            user_text = ""
            for m in reversed(request.messages):
                if m.get("role") == "user":
                    content = m.get("content", "")
                    if isinstance(content, str):
                        user_text = content
                    break

            logger.info(f"?? User query: {user_text[:100]}...")

            # Build system prompt with date context
            date_context = claude._get_current_date_context()
            system_prompt = request.system or ""
            
            if system_prompt:
                system_prompt = f"{date_context}\n\n{system_prompt}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."

            # Add web search results if enabled and available
            search_results = []
            search_triggered = False
            
            if request.enable_search and claude.is_search_enabled and user_text:
                search_query = claude._detect_search_need(user_text, [])
                search_triggered = search_query is not None
                
                if search_query:
                    logger.info(f"?? Search triggered for: {search_query}")
                    search_results = await claude._search_web(search_query, count=5)
                    
                    if search_results:
                        search_context = "\n\n## Current Web Search Results\n"
                        search_context += f"Recent search results for: '{search_query}'\n\n"
                        for idx, result in enumerate(search_results, 1):
                            search_context += f"{idx}. **{result['title']}**\n"
                            search_context += f"   URL: {result['url']}\n"
                            search_context += f"   {result['description']}\n\n"
                        search_context += "Use these results to provide accurate, up-to-date information. Cite sources when relevant.\n"
                        system_prompt += search_context
                        
                        logger.info(f"? Added {len(search_results)} search results to streaming context")
                    else:
                        logger.warning(f"?? Search triggered but returned 0 results")
                else:
                    logger.debug(f"?? Search not needed for this query")
            elif not request.enable_search:
                logger.debug(f"?? Search disabled by request")
            elif not claude.is_search_enabled:
                logger.warning(f"?? Search requested but Brave API key not configured")

            # Stream Claude's response directly without modification
            logger.info(f"?? Starting stream with model: {claude.active_model}")
            
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=system_prompt,
                messages=request.messages,
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
                'search_used': bool(search_results),
                'search_results_count': len(search_results),
                'search_triggered': search_triggered,
                'conversation_id': request.conversation_id
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
    Stream Claude AI generation using Server-Sent Events (SSE) with optional web search.
    Claude's markdown output is passed through directly without modification.
    """
    claude = get_claude_client()

    if not claude.is_enabled or not claude.client:
        raise HTTPException(
            status_code=503,
            detail="Claude AI is not configured. Add ANTHROPIC_API_KEY to environment."
        )

    logger.info(f"??? Stream generate request (enable_search={request.enable_search}, "
                f"prompt_length={len(request.prompt)})")

    async def generate():
        try:
            logger.info(f"?? Prompt: {request.prompt[:100]}...")

            # Build system prompt with date context
            date_context = claude._get_current_date_context()
            if request.system_prompt:
                system_prompt = f"{date_context}\n\n{request.system_prompt}"
            else:
                system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."

            # Add web search results if enabled and available
            search_results = []
            search_triggered = False
            
            if request.enable_search and claude.is_search_enabled and request.prompt:
                search_query = claude._detect_search_need(request.prompt, [])
                search_triggered = search_query is not None
                
                if search_query:
                    logger.info(f"?? Search triggered for: {search_query}")
                    search_results = await claude._search_web(search_query, count=5)
                    
                    if search_results:
                        search_context = "\n\n## Current Web Search Results\n"
                        search_context += f"Recent search results for: '{search_query}'\n\n"
                        for idx, result in enumerate(search_results, 1):
                            search_context += f"{idx}. **{result['title']}**\n"
                            search_context += f"   URL: {result['url']}\n"
                            search_context += f"   {result['description']}\n\n"
                        search_context += "Use these results to provide accurate, up-to-date information. Cite sources when relevant.\n"
                        system_prompt += search_context
                        
                        logger.info(f"? Added {len(search_results)} search results to streaming context")
                    else:
                        logger.warning(f"?? Search triggered but returned 0 results")
                else:
                    logger.debug(f"?? Search not needed for this query")
            elif not request.enable_search:
                logger.debug(f"?? Search disabled by request")
            elif not claude.is_search_enabled:
                logger.warning(f"?? Search requested but Brave API key not configured")

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
                'search_used': bool(search_results),
                'search_results_count': len(search_results),
                'search_triggered': search_triggered,
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
                    'fallback': True,
                    'search_used': bool(search_results),
                    'search_results_count': len(search_results),
                    'search_triggered': search_triggered
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
        "search_enabled": claude.is_search_enabled,
        "model": claude.active_model if claude.is_enabled else None,
        "supports_streaming": True,
        "format": "Server-Sent Events (SSE)",
        "text_formatting": "raw Claude output (unmodified)",
        "features": {
            "conversation_history": True,
            "web_search": claude.is_search_enabled,
            "markdown": True,
            "aggressive_search_detection": True  # NEW: Using updated detection
        }
    }


# To use these endpoints in your main.py, add:
# from utils.streaming_ai_endpoints import streaming_ai_router
# app.include_router(streaming_ai_router)
