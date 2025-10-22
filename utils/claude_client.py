"""
Claude AI Client for content moderation and AI features
"""
import os
from typing import Optional
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

# Optional smart spacing flag (disabled by default for safety)
ENABLE_SMART_SPACING = os.getenv("ENABLE_SMART_SPACING", "false").lower() == "true"

# Try to import word segmentation lazily
_ws_loaded = False
try:
    from wordsegment import load as _ws_load, segment as _ws_segment
    def _ensure_ws_loaded():
        global _ws_loaded
        if not _ws_loaded:
            try:
                _ws_load()
                _ws_loaded = True
            except Exception:
                _ws_loaded = False
except Exception:
    def _ensure_ws_loaded():
        # wordsegment not available
        return
    _ws_segment = None  # type: ignore


def _segment_run_on_words(text: str) -> str:
    """Best-effort segmentation of very long run-on alphabetic tokens.
    Only applied when ENABLE_SMART_SPACING=true and wordsegment is available.
    """
    if not ENABLE_SMART_SPACING or _ws_segment is None:
        return text

    _ensure_ws_loaded()
    if not _ws_loaded:
        return text

    def should_segment(token: str) -> bool:
        # Segment only long alphabetic tokens with no internal spaces
        # Avoid tokens containing digits, underscores, or obvious code
        return token.isalpha() and len(token) >= 12

    # Split but keep delimiters
    parts = re.split(r"(\s+)", text)
    out_parts = []
    for part in parts:
        if part and not part.isspace() and should_segment(part):
            try:
                words = _ws_segment(part.lower())
                segmented = " ".join(words)
                # Preserve leading capitalization
                if part[0].isupper():
                    segmented = segmented.capitalize()
                out_parts.append(segmented)
            except Exception:
                out_parts.append(part)
        else:
            out_parts.append(part)
    return "".join(out_parts)


def format_text(text: str) -> str:
    """
    Format text to fix common spacing and grammar issues in Claude responses.
    Shared between streaming and non-streaming endpoints.
    """
    if not text or len(text) < 2:
        return text
    
    # Common patterns where spaces may be missing
    
    # 1. After punctuation marks followed by a capital letter or lowercase letter
    text = re.sub(r'\.([A-Z])', r'. \1', text)  # Period followed by capital
    text = re.sub(r'\.([a-z])', r'. \1', text)  # Period followed by lowercase
    text = re.sub(r'\!([A-Za-z])', r'! \1', text)  # Exclamation mark
    text = re.sub(r'\?([A-Za-z])', r'? \1', text)  # Question mark
    text = re.sub(r',([A-Za-z])', r', \1', text)  # Comma
    text = re.sub(r':([A-Za-z])', r': \1', text)  # Colon
    text = re.sub(r';([A-Za-z])', r'; \1', text)  # Semicolon
    
    # 2. Around parentheses, brackets, and braces
    text = re.sub(r'([A-Za-z0-9])\(', r'\1 (', text)  # Before opening parenthesis
    text = re.sub(r'\)([A-Za-z0-9])', r') \1', text)  # After closing parenthesis
    text = re.sub(r'([A-Za-z0-9])\[', r'\1 [', text)  # Before opening bracket
    text = re.sub(r'\]([A-Za-z0-9])', r'] \1', text)  # After closing bracket
    text = re.sub(r'([A-Za-z0-9])\{', r'\1 {', text)  # Before opening brace
    text = re.sub(r'\}([A-Za-z0-9])', r'} \1', text)  # After closing brace
    
    # 3. Around quotes
    text = re.sub(r'([A-Za-z0-9])"([A-Za-z0-9])', r'\1" \2', text)  # Between words and double quotes
    text = re.sub(r'([A-Za-z0-9])\'([A-Za-z0-9])', r'\1\' \2', text)  # Between words and single quotes
    
    # 4. Fix spacing around dashes and hyphens
    text = re.sub(r'([A-Za-z0-9])--([A-Za-z0-9])', r'\1 -- \2', text)  # Em dash
    text = re.sub(r'([A-Za-z0-9])–([A-Za-z0-9])', r'\1 – \2', text)  # En dash
    
    # 5. Fix spacing between sentences that might be run together
    text = re.sub(r'([a-z])\.([A-Z])', r'\1. \2', text)  # Lowercase period uppercase
    
    # 6. Fix periods without spaces in acronyms
    text = re.sub(r'([a-z])\.([A-Z][a-z])', r'\1. \2', text)  # Period between lowercase and "Title case"
    
    # 7. Fix spacing in lists and enumerations
    text = re.sub(r'(\d+)\.([\w])', r'\1. \2', text)  # Number followed by period and word
    
    # 8. Fix spaces between sections of a document
    text = re.sub(r'([a-z])\n([A-Z])', r'\1\n\n\2', text)  # New paragraph should have blank line
    
    # 9. Make sure there's no double spaces
    text = re.sub(r' {2,}', ' ', text)

    # 10. Optional: smart segmentation of long run-on words
    text = _segment_run_on_words(text)
    
    return text


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
    
    def _get_current_date_context(self) -> str:
        """Get current date and time context for Claude"""
        now = datetime.now()
        return f"The current date and time is {now.strftime('%A, %B %d, %Y at %I:%M %p')}."
    
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
        
        # Prepare system prompt with date context
        date_context = self._get_current_date_context()
        if system_prompt:
            full_system_prompt = f"{date_context}\n\n{system_prompt}"
        else:
            full_system_prompt = f"{date_context}\n\nYou are a helpful AI assistant."
        
        try:
            message = self.client.messages.create(
                model=self.active_model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=full_system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Log response stats
            response_text = message.content[0].text
            logger.info(f"Claude response received (length: {len(response_text)}, spaces: {response_text.count(' ')})")
            
            # Apply text formatting to fix spacing/grammar issues
            formatted_text = format_text(response_text)
            
            # Log if formatting made changes
            if formatted_text != response_text:
                logger.info("Text formatting applied to fix grammar/spacing issues")
            
            return formatted_text
            
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
                    system=full_system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                logger.info(f"✓ Successfully switched to fallback model: {self.active_model}")
                
                # Apply text formatting to fix spacing/grammar issues
                response_text = message.content[0].text
                formatted_text = format_text(response_text)
                
                return formatted_text
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
