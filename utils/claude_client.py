"""
Claude AI Client for content moderation and AI features
"""
import os
from typing import Optional, List, Dict
from datetime import datetime
import anthropic
import logging
import json
import re

logger = logging.getLogger(__name__)

# Model configuration - Use the latest available Claude model
# Updated: January 2025
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"  # Latest Claude 4.5 Sonnet
FALLBACK_MODEL = "claude-3-5-sonnet-20241022"  # Fallback to Claude 3.5 if 4.5 unavailable


def format_text(text: str) -> str:
    """
    Legacy formatter (unused by streaming and non-streaming paths now).
    Kept for backward compatibility; returns text unchanged.
    """
    return text


class ClaudeClient:
    """
    Client for Claude AI API integration using Anthropic SDK.
    
    Features:
    - Content moderation
    - Smart replies
    - Message summarization
    - Spam detection
    - Conversation history (NEW)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.active_model = CLAUDE_MODEL
        # NEW: Store conversations by session/user ID
        self.conversations: Dict[str, List[Dict]] = {}
        
        if not self.api_key:
            logger.warning("Claude API key not found - AI features disabled")
        else:
            try:
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"✓ Claude AI client initialized with model: {self.active_model}")
            except Exception as e:
                logger.error(f"Failed to initialize Claude client: {e}")
    
    @property
    def is_enabled(self) -> bool:
        """Check if Claude client is enabled"""
        return self.client is not None
    
    def _get_current_date_context(self) -> str:
        """Get current date and time context for Claude"""
        now = datetime.now()
        return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        conversation_id: Optional[str] = None  # NEW: Optional conversation tracking
    ) -> str:
        """
        Generate a response from Claude with optional conversation history.
        
        Args:
            prompt: User's message
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0-1)
            system_prompt: System instructions
            conversation_id: Optional unique ID to maintain conversation history across calls
        
        Returns:
            Claude's response text
        
        Note: Backward compatible - if conversation_id is not provided, works exactly as before
        """
        if not self.is_enabled:
            return "Claude AI is not configured. Add ANTHROPIC_API_KEY to enable AI features."
        
        # Prepare system prompt with date context
        date_context = self._get_current_date_context()
        if system_prompt:
            full_system_prompt = f"{date_context}\n\n{system_prompt}"
        else:
            full_system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."
        
        # NEW: Get or create conversation history
        if conversation_id:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []
            messages = self.conversations[conversation_id].copy()
            # Add current user message
            messages.append({"role": "user", "content": prompt})
        else:
            # Backward compatible: single message without history
            messages = [{"role": "user", "content": prompt}]
        
        try:
            message = self.client.messages.create(
                model=self.active_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=full_system_prompt,
                messages=messages
            )
            response_text = message.content[0].text
            
            # NEW: Save conversation history if tracking is enabled
            if conversation_id:
                self.conversations[conversation_id].append({"role": "user", "content": prompt})
                self.conversations[conversation_id].append({"role": "assistant", "content": response_text})
                logger.info(
                    "Claude response (len=%d, conversation=%s, history_len=%d)",
                    len(response_text),
                    conversation_id,
                    len(self.conversations[conversation_id])
                )
            else:
                logger.info(
                    "Claude response received (len=%d, spaces=%d)",
                    len(response_text),
                    response_text.count(" "),
                )
            
            return response_text
            
        except anthropic.NotFoundError as e:
            # Model not found - try fallback
            logger.warning("Model %s not found, trying fallback: %s", self.active_model, FALLBACK_MODEL)
            logger.error("Original error: %s", e)
            try:
                self.active_model = FALLBACK_MODEL
                message = self.client.messages.create(
                    model=self.active_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=full_system_prompt,
                    messages=messages
                )
                logger.info("✓ Switched to fallback model: %s", self.active_model)
                response_text = message.content[0].text
                
                # NEW: Save to history if tracking
                if conversation_id:
                    self.conversations[conversation_id].append({"role": "user", "content": prompt})
                    self.conversations[conversation_id].append({"role": "assistant", "content": response_text})
                
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
    
    # NEW: Conversation management methods
    def clear_conversation(self, conversation_id: str) -> None:
        """
        Clear conversation history for a specific conversation ID.
        
        Args:
            conversation_id: The conversation to clear
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Cleared conversation history for: {conversation_id}")
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Get conversation history for a specific conversation ID.
        
        Args:
            conversation_id: The conversation to retrieve
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        return self.conversations.get(conversation_id, [])
    
    def get_conversation_count(self, conversation_id: str) -> int:
        """
        Get the number of messages in a conversation.
        
        Args:
            conversation_id: The conversation to count
            
        Returns:
            Number of messages (user + assistant)
        """
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
            # No conversation_id - each moderation is independent
            response = self.generate_response(
                prompt=f"Message to moderate: {content}",
                max_tokens=200,
                temperature=0.3,
                system_prompt=system_prompt,
                conversation_id=None
            )
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
    
    def summarize_conversation(self, messages: list) -> str:
        """Summarize a conversation."""
        if not self.is_enabled:
            return "Summarization not available"
        conversation = "\n".join([
            f"{msg['username']}: {msg['content']}"
            for msg in messages[-20:]
        ])
        prompt = f"Summarize this chat conversation in 2-3 sentences:\n\n{conversation}"
        return self.generate_response(prompt, max_tokens=150, temperature=0.5)
    
    def suggest_reply(self, context: str, user_message: str) -> str:
        """Suggest a smart reply based on context."""
        if not self.is_enabled:
            return "Smart replies not available"
        system_prompt = "You are a friendly chat assistant. Generate a natural, conversational reply."
        prompt = f"Context: {context}\n\nMessage: {user_message}\n\nSuggest a friendly reply:"
        return self.generate_response(prompt, max_tokens=100, temperature=0.8, system_prompt=system_prompt)
    
    def get_model_info(self) -> dict:
        """Get information about the active model"""
        return {
            "active_model": self.active_model,
            "fallback_model": FALLBACK_MODEL,
            "is_enabled": self.is_enabled,
            "active_conversations": len(self.conversations)  # NEW: Track conversation count
        }


# Global instance
_claude_client = None


def get_claude_client() -> ClaudeClient:
    """Get or create Claude client singleton"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
