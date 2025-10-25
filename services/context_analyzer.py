from typing import Dict, List, Optional
from app.models.chat_models import Message
import re

class ContextAnalyzer:
    """Analyzes conversation context to determine formatting needs."""

    def analyze(self, user_input: str, history: List[Message]) -> Dict:
        """Main analysis function."""
        return {
            'is_casual': self._is_casual_conversation(user_input),
            'is_technical': self._is_technical_query(user_input),
            'needs_structure': self._needs_structured_format(user_input),
            'is_emotional': self._is_emotional_content(user_input),
            'needs_code': self._requires_code_example(user_input),
            'conversation_tone': self._analyze_tone(history)
        }

    def _is_casual_conversation(self, text: str) -> bool:
        """Detect casual language patterns."""
        text_lower = text.lower()
        casual_indicators = ['hey', 'hi', 'lol', 'thanks', '!', '?', 'yo', 'sup', 'thx']
        return any(indicator in text_lower for indicator in casual_indicators)

    def _is_technical_query(self, text: str) -> bool:
        """Detect technical content."""
        technical_keywords = [
            'python', 'javascript', 'fastapi', 'react', 'docker', 'kubernetes',
            'sql', 'nosql', 'api', 'endpoint', 'websocket', 'json', 'yaml',
            'function', 'class', 'method', 'variable', 'error', 'exception',
            'bug', 'debug', 'install', 'configure', 'deploy'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in technical_keywords) or '```' in text

    def _needs_structured_format(self, text: str) -> bool:
        """Determine if the input suggests a need for a list, table, or steps."""
        structured_keywords = ['steps', 'list', 'how to', 'compare', 'difference', 'what are']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in structured_keywords)

    def _is_emotional_content(self, text: str) -> bool:
        """Detect emotionally charged words."""
        emotional_words = [
            'frustrated', 'angry', 'sad', 'happy', 'excited', 'love', 'hate',
            'amazing', 'terrible', 'awful', 'fantastic'
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in emotional_words)

    def _requires_code_example(self, text: str) -> bool:
        """Check if the user is asking for a code example."""
        code_request_patterns = [
            r'show me an example',
            r'code for',
            r'how do I write',
            r'sample code',
            r'snippet for'
        ]
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in code_request_patterns) or self._is_technical_query(text)

    def _analyze_tone(self, history: List[Message]) -> str:
        """Analyze the overall tone of the conversation history."""
        if not history:
            return "neutral"

        emotional_score = 0
        for message in history:
            if self._is_emotional_content(message.content):
                emotional_score += 1
            if self._is_casual_conversation(message.content):
                emotional_score -= 0.5

        if emotional_score > 2:
            return "emotional"
        if emotional_score < -1:
            return "casual"
        
        technical_score = 0
        for message in history:
            if self._is_technical_query(message.content):
                technical_score += 1
        
        if technical_score >= 2:
            return "technical"

        return "neutral"
