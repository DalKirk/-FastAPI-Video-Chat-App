"""
Claude AI Client for content moderation and AI features
"""
import os
from typing import Optional
import anthropic
import logging
import json

logger = logging.getLogger(__name__)

# Model configuration - Use the latest available Claude model
# Updated: January 2025
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"  # Latest Claude 4.5 Sonnet
FALLBACK_MODEL = "claude-3-5-sonnet-20241022"  # Fallback to Claude 3.5 if 4.5 unavailable


class ClaudeClient:
    """
    Client for Claude AI API integration using Anthropic SDK.
    
    Features:
    - Content moderation
    - Smart replies
    - Message summarization
    - Spam detection
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude client with API key"""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        self.active_model = CLAUDE_MODEL
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
    
    def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate a response from Claude.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            temperature: Creativity (0.0-1.0)
            system_prompt: Optional system instructions
        
        Returns:
            Generated text response
        """
        if not self.is_enabled:
            return "Claude AI is not configured. Add ANTHROPIC_API_KEY to enable AI features."
        
        try:
            message = self.client.messages.create(
                model=self.active_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt if system_prompt else "You are a helpful AI assistant.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text
            
        except anthropic.NotFoundError as e:
            # Model not found - try fallback
            logger.warning(f"Model {self.active_model} not found, trying fallback: {FALLBACK_MODEL}")
            logger.error(f"Original error: {e}")
            
            try:
                self.active_model = FALLBACK_MODEL
                message = self.client.messages.create(
                    model=self.active_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt if system_prompt else "You are a helpful AI assistant.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                logger.info(f"✓ Successfully switched to fallback model: {self.active_model}")
                return message.content[0].text
            except Exception as fallback_error:
                logger.error(f"Fallback model also failed: {fallback_error}")
                return f"Error: Model not available. Please check Anthropic API status."
                
        except anthropic.AuthenticationError as e:
            logger.error(f"Authentication error: {e}")
            return "Error: Invalid API key. Please check your ANTHROPIC_API_KEY."
            
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit error: {e}")
            return "Error: Rate limit exceeded. Please try again later."
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error generating response: {str(e)}"
    
    def moderate_content(self, content: str) -> dict:
        """
        Moderate content for inappropriate material.
        
        Returns:
            {
                "is_safe": bool,
                "reason": str,
                "confidence": float
            }
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
            response = self.generate_response(
                prompt=f"Message to moderate: {content}",
                max_tokens=200,
                temperature=0.3,
                system_prompt=system_prompt
            )
            
            # Parse JSON response
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Content moderation error: {e}")
            # Fail open - allow content if moderation fails
            return {"is_safe": True, "reason": f"Moderation error: {str(e)}", "confidence": 0.0}
    
    def detect_spam(self, content: str) -> bool:
        """
        Detect if message is spam.
        
        Returns:
            True if spam detected, False otherwise
        """
        if not self.is_enabled:
            return False
        
        moderation = self.moderate_content(content)
        return not moderation.get("is_safe", True) and "spam" in moderation.get("reason", "").lower()
    
    def summarize_conversation(self, messages: list) -> str:
        """
        Summarize a conversation.
        
        Args:
            messages: List of message dicts with 'username' and 'content'
        
        Returns:
            Summary text
        """
        if not self.is_enabled:
            return "Summarization not available"
        
        conversation = "\n".join([
            f"{msg['username']}: {msg['content']}"
            for msg in messages[-20:]  # Last 20 messages
        ])
        
        prompt = f"Summarize this chat conversation in 2-3 sentences:\n\n{conversation}"
        return self.generate_response(prompt, max_tokens=150, temperature=0.5)
    
    def suggest_reply(self, context: str, user_message: str) -> str:
        """
        Suggest a smart reply based on context.
        
        Args:
            context: Recent conversation context
            user_message: Message to reply to
        
        Returns:
            Suggested reply
        """
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
            "is_enabled": self.is_enabled
        }


# Global instance
_claude_client = None


def get_claude_client() -> ClaudeClient:
    """Get or create Claude client singleton"""
    global _claude_client
    if _claude_client is None:
        _claude_client = ClaudeClient()
    return _claude_client
