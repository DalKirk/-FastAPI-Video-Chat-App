"""
Claude AI Client for content moderation and AI features with Web Search
"""
import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import anthropic
import logging
import json
import httpx

logger = logging.getLogger(__name__)

# Model configuration
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
FALLBACK_MODEL = "claude-3-5-sonnet-20241022"


class ClaudeClient:
    """
    Client for Claude AI API integration with conversation history and web search.
    
    Features:
    - Content moderation
    - Smart replies
    - Message summarization
    - Spam detection
    - Conversation history
    - Web search integration
    """
    
    def __init__(self, api_key: Optional[str] = None, brave_api_key: Optional[str] = None):
        """Initialize Claude client with API keys"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.brave_api_key = brave_api_key or os.getenv("BRAVE_SEARCH_API_KEY")
        self.client = None
        self.active_model = CLAUDE_MODEL
        self.conversations: Dict[str, List[Dict]] = {}
        
        if not self.api_key:
            logger.warning("Claude API key not found - AI features disabled")
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"✓ Claude AI client initialized with model: {self.active_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
        
        if not self.brave_api_key:
            logger.warning("Brave Search API key not found - Web search disabled")
        else:
            logger.info("✓ Web search enabled via Brave Search API")
    
    @property
    def is_enabled(self) -> bool:
        """Check if Claude client is enabled"""
        return self.client is not None
    
    @property
    def is_search_enabled(self) -> bool:
        """Check if web search is enabled"""
        return self.brave_api_key is not None
    
    def _get_current_date_context(self) -> str:
        """Get current date and time context for Claude"""
        now = datetime.now()
        return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."
    
    async def _search_web(self, query: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search using Brave Search API.
        
        Args:
            query: Search query
            count: Number of results to return (max 20)
            
        Returns:
            List of search results with title, url, description
        """
        if not self.is_search_enabled:
            logger.warning("Web search attempted but API key not configured")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    headers={
                        "Accept": "application/json",
                        "X-Subscription-Token": self.brave_api_key
                    },
                    params={
                        "q": query,
                        "count": min(count, 20)
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract relevant results
                results = []
                for item in data.get("web", {}).get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "description": item.get("description", "")
                    })
                
                logger.info(f"🔍 Web search for '{query}' returned {len(results)} results")
                return results
                
        except httpx.TimeoutException:
            logger.error(f"Web search timeout for query: {query}")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"Web search HTTP error: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return []
    
    def _detect_search_need(self, prompt: str, conversation_history: List[Dict]) -> Optional[str]:
        """
        Detect if the query requires web search.
        Defaults to searching for factual queries; skips search for creative tasks.
        
        Returns:
            Search query string if search is needed, None otherwise
        """
        prompt_lower = prompt.lower()
        
        # Skip search for creative/generative tasks
        creative_indicators = [
            "write a", "create a", "generate a", "compose a", "draft a",
            "make a", "build a", "design a",
            "tell me a story", "poem", "song", "joke", "riddle",
            "translate", "rewrite", "rephrase", "paraphrase",
            "summarize this text", "summarize the following"
        ]
        
        # Skip search for explanatory/educational questions about concepts
        concept_indicators = [
            "explain how", "explain why", "how does", "why does",
            "what is the difference between", "compare",
            "teach me", "help me understand"
        ]
        
        # Skip search for code generation
        code_indicators = [
            "write code", "write a function", "write a script",
            "create a function", "code for", "program that",
            "regex for", "sql query", "fix this code", "debug this"
        ]
        
        # Check if it's a creative/explanatory/code task
        all_skip_indicators = creative_indicators + concept_indicators + code_indicators
        if any(indicator in prompt_lower for indicator in all_skip_indicators):
            logger.debug(f"ℹ️  Skipping search for creative/explanatory task: {prompt[:50]}...")
            return None
        
        # Default: enable search for factual queries
        logger.info(f"🔍 Search enabled for factual query: {prompt[:60]}...")
        return prompt
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        conversation_id: Optional[str] = None,
        enable_search: bool = True
    ) -> str:
        """
        Generate a response from Claude with conversation history and optional web search.
        
        Args:
            prompt: User's message
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)
            system_prompt: System instructions
            conversation_id: Unique ID to maintain conversation history
            enable_search: Whether to enable automatic web search
        
        Returns:
            Claude's response text
        """
        if not self.is_enabled:
            return "Claude AI is not configured. Add ANTHROPIC_API_KEY to enable AI features."
        
        # Get or create conversation history
        if conversation_id:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            messages = self.conversations[conversation_id].copy()
        else:
            messages = []
        
        # Detect if web search is needed
        search_results = []
        if enable_search and self.is_search_enabled:
            search_query = self._detect_search_need(prompt, messages)
            if search_query:
                search_results = await self._search_web(search_query, count=5)
        
        # Prepare system prompt with date context and search results
        date_context = self._get_current_date_context()
        full_system_prompt = date_context
        
        if system_prompt:
            full_system_prompt += f"\n\n{system_prompt}"
        else:
            full_system_prompt += "\n\nYou are a helpful AI assistant."
        
        # Add search results to context if available
        if search_results:
            search_context = "\n\n## Current Web Search Results\n"
            search_context += f"The following are recent search results for: '{search_query}'\n\n"
            for idx, result in enumerate(search_results, 1):
                search_context += f"{idx}. **{result['title']}**\n"
                search_context += f"   URL: {result['url']}\n"
                search_context += f"   {result['description']}\n\n"
            search_context += (
                "Use these search results to provide accurate, up-to-date information. "
                "Cite sources by mentioning the title or URL when relevant.\n"
            )
            full_system_prompt += search_context
            logger.info(f"✓ Added {len(search_results)} search results to context")
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})
        
        try:
            message = self.client.messages.create(
                model=self.active_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=full_system_prompt,
                messages=messages
            )
            response_text = message.content[0].text
            
            # Save conversation history
            if conversation_id:
                self.conversations[conversation_id].append(
                    {"role": "user", "content": prompt}
                )
                self.conversations[conversation_id].append(
                    {"role": "assistant", "content": response_text}
                )
            
            logger.info(
                "✓ Claude response received (len=%d, history_length=%d, search_used=%s)",
                len(response_text),
                len(self.conversations.get(conversation_id, [])),
                bool(search_results)
            )
            return response_text
            
        except anthropic.NotFoundError as e:
            logger.warning("Model %s not found, trying fallback: %s", self.active_model, FALLBACK_MODEL)
            try:
                self.active_model = FALLBACK_MODEL
                message = self.client.messages.create(
                    model=self.active_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=full_system_prompt,
                    messages=messages
                )
                response_text = message.content[0].text
                
                if conversation_id:
                    self.conversations[conversation_id].append(
                        {"role": "user", "content": prompt}
                    )
                    self.conversations[conversation_id].append(
                        {"role": "assistant", "content": response_text}
                    )
                
                logger.info("✓ Switched to fallback model: %s", self.active_model)
                return response_text
            except Exception as fallback_error:
                logger.error("Fallback model also failed: %s", fallback_error)
                return "Error: Model not available. Please check Anthropic API status."
                
        except anthropic.AuthenticationError as e:
            logger.error("Authentication error: %s", e)
            return "Error: Invalid API key. Please check your ANTHROPIC_API_KEY."
            
        except anthropic.RateLimitError as e:
            logger.error("Rate limit error: %s", e)
            return "Error: Rate limit exceeded. Please try again later."
            
        except Exception as e:
            logger.error("Claude API error: %s", e)
            return f"Error generating response: {str(e)}"
    
    def clear_conversation(self, conversation_id: str) -> None:
        """Clear conversation history for a specific conversation ID"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation history for: {conversation_id}")
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history for a specific conversation ID"""
        return self.conversations.get(conversation_id, [])
    
    def get_conversation_count(self, conversation_id: str) -> int:
        """Get the number of messages in a conversation"""
        return len(self.conversations.get(conversation_id, []))
    
    def moderate_content(self, content: str) -> dict:
        """
        Moderate content for inappropriate material.
        Returns a JSON-compatible dict. On failure, fails open.
        
        Note: Does NOT use conversation history (each moderation is independent)
        """
        if not self.is_enabled:
            return {"is_safe": True, "reason": "Moderation disabled", "confidence": 0.0}
        
        system_prompt = """You are a content moderator. Analyze the following message and determine if it contains:
- Hate speech
- Harassment or bullying
- Explicit sexual content
- Violence or threats
- Spam or scams
- Personal information (PII)

Respond ONLY with a JSON object:
{
    "is_safe": true/false,
    "reason": "brief explanation",
    "confidence": 0.0-1.0
}"""
        
        try:
            # Create a temporary sync client for moderation
            import asyncio
            response = asyncio.run(self.generate_response(
                prompt=f"Message to moderate: {content}",
                max_tokens=200,
                temperature=0.3,
                system_prompt=system_prompt,
                conversation_id=None,
                enable_search=False
            ))
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error("Content moderation error: %s", e)
            return {"is_safe": True, "reason": f"Moderation error: {str(e)}", "confidence": 0.0}
    
    def detect_spam(self, content: str) -> bool:
        """Detect if message is spam."""
        if not self.is_enabled:
            return False
        moderation = self.moderate_content(content)
        return not moderation.get("is_safe", True) and "spam" in moderation.get("reason", "").lower()
    
    async def summarize_conversation(self, messages: list) -> str:
        """Summarize a conversation."""
        if not self.is_enabled:
            return "Summarization not available"
        conversation = "\n".join([
            f"{msg['username']}: {msg['content']}"
            for msg in messages[-20:]
        ])
        prompt = f"Summarize this chat conversation in 2-3 sentences:\n\n{conversation}"
        return await self.generate_response(
            prompt, 
            max_tokens=150, 
            temperature=0.5,
            enable_search=False
        )
    
    async def suggest_reply(self, context: str, user_message: str) -> str:
        """Suggest a smart reply based on context."""
        if not self.is_enabled:
            return "Smart replies not available"
        system_prompt = "You are a friendly chat assistant. Generate a natural, conversational reply."
        prompt = f"Context: {context}\n\nMessage: {user_message}\n\nSuggest a friendly reply:"
        return await self.generate_response(
            prompt, 
            max_tokens=100, 
            temperature=0.8, 
            system_prompt=system_prompt,
            enable_search=False
        )
    
    def get_model_info(self) -> dict:
        """Get information about the active model"""
        return {
            "active_model": self.active_model,
            "fallback_model": FALLBACK_MODEL,
            "is_enabled": self.is_enabled,
            "is_search_enabled": self.is_search_enabled,
            "active_conversations": len(self.conversations)
        }


# Global instance
_claude_client = None


def get_claude_client() -> ClaudeClient:
    """Get or create Claude client singleton"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
