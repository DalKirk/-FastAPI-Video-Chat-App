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
import os
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

# Brave Search Integration
BRAVE_SEARCH_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

def brave_enabled() -> bool:
    """Check if Brave Search is configured"""
    return bool(BRAVE_SEARCH_KEY)

async def brave_search(query: str, count: int = 5) -> List[Dict[str, Any]]:
    """Fetch web search results from Brave API"""
    if not brave_enabled() or not query:
        return []
    
    headers = {"X-Subscription-Token": BRAVE_SEARCH_KEY}
    params = {"q": query, "count": count, "source": "web"}
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params
            )
            resp.raise_for_status()
            data = resp.json()
            web_results = (data.get("web", {}) or {}).get("results", []) or []
            
            results = []
            for r in web_results[:count]:
                results.append({
                    "title": r.get("title", "").strip(),
                    "url": r.get("url", "").strip(),
                    "snippet": r.get("snippet", "").strip(),
                })
            return results
    except Exception as e:
        logger.warning(f"Brave search failed: {e}")
        return []

def format_search_context(results: List[Dict[str, Any]]) -> str:
    """Format search results for injection into system prompt"""
    if not results:
        return ""
    
    lines = ["Web context (Brave):"]
    for i, r in enumerate(results, 1):
        title = r.get("title", "")
        url = r.get("url", "")
        snippet = r.get("snippet", "")
        lines.append(f"{i}. {title} - {snippet} [ref: {url}]")
    
    lines.append("\nCite sources with [ref: URL]. If details conflict, say so explicitly.")
    return "\n".join(lines)

# Create router for streaming AI endpoints
streaming_ai_router = APIRouter(prefix="/ai/stream", tags=["AI Streaming"])


class StreamChatRequest(BaseModel):
    """Request for streaming chat"""
    messages: List[Dict[str, str]]  # [{"role": "user", "content": "..."}, ...]
    max_tokens: int = 2048
    temperature: float = 0.7
    system: Optional[str] = None
    conversation_id: Optional[str] = None  # Conversation tracking
    enable_search: Optional[bool] = True  # Enable web search


class StreamGenerateRequest(BaseModel):
    """Request for streaming generation"""
    prompt: str
    max_tokens: int = 2048
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    conversation_id: Optional[str] = None  # Conversation tracking
    enable_search: Optional[bool] = True  # Enable web search


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
    logger.info(f"Stream chat request (conversation_id={request.conversation_id}, messages={len(request.messages)})")

    async def generate():
        try:
            # Get or create conversation history
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
            
            logger.info(f"Using {len(conversation_messages)} messages in conversation history")
            
            # Extract last user message for search query
            user_text = ""
            for m in reversed(request.messages):
                if m.get("role") == "user":
                    content = m.get("content")
                    if isinstance(content, str):
                        user_text = content
                    elif isinstance(content, list):
                        user_text = " ".join([
                            c.get("text", "") 
                            for c in content 
                            if isinstance(c, dict) and c.get("type") == "text"
                        ])
                    break
            
            # Build system prompt with date context
            date_context = claude._get_current_date_context()
            injected_system = request.system or ""
            
            # Inject Brave search results if enabled
            search_results = []
            if request.enable_search and brave_enabled() and user_text:
                search_results = await brave_search(user_text, count=5)
                search_context = format_search_context(search_results)
                if search_context:
                    if injected_system:
                        injected_system = f"{injected_system}\n\n{search_context}"
                    else:
                        injected_system = search_context
            
            logger.info(
                f"stream_chat: enable_search={request.enable_search}, "
                f"query_present={bool(user_text)}, "
                f"results={len(search_results)}"
            )
            
            # Add markdown formatting instructions
            markdown_instructions = (
                "\n\nIMPORTANT FORMATTING RULES:\n"
                "- When creating lists, use proper markdown with ONE ITEM PER LINE\n"
                "- For bullet points, use this format:\n"
                "  - First item\n"
                "  - Second item\n"
                "  - Third item\n"
                "- For numbered lists, use this format:\n"
                "  1. First item\n"
                "  2. Second item\n"
                "  3. Third item\n"
                "- NEVER put multiple list items on the same line\n"
                "- NEVER use unicode bullets, always use markdown dashes (-)\n"
                "- Add blank lines before and after lists\n"
            )
            
            if injected_system:
                injected_system = f"{date_context}\n\n{injected_system}{markdown_instructions}"
            else:
                injected_system = f"{date_context}\n\nYou are a helpful AI assistant.{markdown_instructions}"

            # Stream Claude's response with full conversation history
            logger.info(f"Starting stream with model: {claude.active_model}")
            
            full_response = ""  # Track full response for saving to history
            
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=injected_system,  # THE CRITICAL CHANGE - use injected_system!
                messages=conversation_messages,  # Use full conversation history
            ) as stream:
                chunk_count = 0
                for text in stream.text_stream:
                    chunk = text or ""
                    chunk_count += 1
                    full_response += chunk  # Accumulate response
                    yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                
                logger.info(f"Stream completed ({chunk_count} chunks)")
            
            # Save conversation history
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
                logger.info(f"Saved to conversation {request.conversation_id} (total: {len(claude.conversations[request.conversation_id])} messages)")

            # Send completion with metadata
            completion_data = {
                'type': 'done', 
                'model': claude.active_model,
                'conversation_id': request.conversation_id,
                'conversation_length': len(claude.conversations.get(request.conversation_id, []))
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except anthropic.NotFoundError as e:
            logger.error(f"Model not found: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': f'Model not found: {str(e)}'})}\n\n"
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
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

    logger.info(f"Stream generate request (prompt_length={len(request.prompt)})")

    async def generate():
        try:
            # Build system prompt with date context
            date_context = claude._get_current_date_context()
            injected_system = request.system_prompt or ""
            
            # Inject Brave search results if enabled
            search_results = []
            if request.enable_search and brave_enabled() and request.prompt:
                search_results = await brave_search(request.prompt, count=5)
                search_context = format_search_context(search_results)
                if search_context:
                    if injected_system:
                        injected_system = f"{injected_system}\n\n{search_context}"
                    else:
                        injected_system = search_context
            
            logger.info(
                f"stream_generate: enable_search={request.enable_search}, "
                f"prompt_present={bool(request.prompt)}, "
                f"results={len(search_results)}"
            )
            
            if injected_system:
                injected_system = f"{date_context}\n\n{injected_system}"
            else:
                injected_system = f"{date_context}\n\nYou are a helpful AI assistant."

            messages = [{"role": "user", "content": request.prompt}]

            # Stream Claude's response
            logger.info(f"Starting stream with model: {claude.active_model}")
            
            with claude.client.messages.stream(
                model=claude.active_model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=injected_system,  # THE CRITICAL CHANGE - use injected_system!
                messages=messages,
            ) as stream:
                chunk_count = 0
                for text in stream.text_stream:
                    chunk = text or ""
                    chunk_count += 1
                    yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                
                logger.info(f"Stream completed ({chunk_count} chunks)")

            # Send completion with metadata
            completion_data = {
                'type': 'done', 
                'model': claude.active_model,
                'conversation_id': request.conversation_id
            }
            yield f"data: {json.dumps(completion_data)}\n\n"

        except anthropic.NotFoundError:
            # Fallback to backup model
            logger.warning(f"Model not found, trying fallback")
            try:
                claude.active_model = claude.get_model_info()["fallback_model"]
                logger.info(f"Switched to fallback model: {claude.active_model}")
                
                with claude.client.messages.stream(
                    model=claude.active_model,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    system=injected_system,
                    messages=messages,
                ) as stream:
                    chunk_count = 0
                    for text in stream.text_stream:
                        chunk = text or ""
                        chunk_count += 1
                        yield f"data: {json.dumps({'text': chunk, 'type': 'content'})}\n\n"
                    
                    logger.info(f"Fallback stream completed ({chunk_count} chunks)")
                
                # Send fallback completion
                fallback_data = {
                    'type': 'done', 
                    'model': claude.active_model, 
                    'fallback': True
                }
                yield f"data: {json.dumps(fallback_data)}\n\n"
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
                yield f"data: {json.dumps({'type': 'error', 'error': f'Both models failed: {str(fallback_error)}'})}\n\n"
        except anthropic.AuthenticationError:
            logger.error(f"Authentication error")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Invalid API key'})}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}", exc_info=True)
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
        "brave_search_enabled": brave_enabled(),  # NEW: Expose Brave status
        "features": {
            "conversation_history": True,
            "markdown": True,
            "web_search": brave_enabled()  # NEW: Web search feature
        }
    }


# To use these endpoints in your main.py, add:
# from utils.streaming_ai_endpoints import streaming_ai_router
# app.include_router(streaming_ai_router)
