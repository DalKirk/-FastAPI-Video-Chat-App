from typing import Dict, List, Optional
from app.models.chat_models import Message
from services.context_analyzer import ContextAnalyzer
from services.format_selector import FormatSelector, FormatType
from services.response_formatter import ResponseFormatter
from utils.claude_client import get_claude_client
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Main service that orchestrates AI response generation with context-aware formatting."""

    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
        self.format_selector = FormatSelector()
        self.formatter = ResponseFormatter()
        self.claude_client = get_claude_client()

    async def generate_response(self, user_input: str, history: List[Message]) -> Dict:
        """
        Main pipeline for generating formatted AI responses.
        
        Args:
            user_input: The user's current message/query.
            history: List of previous Message objects in the conversation.
            
        Returns:
            A dictionary containing the formatted response, format type, and metadata.
        """
        try:
            # Step 1: Analyze conversation context
            context = self.context_analyzer.analyze(user_input, history)
            logger.info(f"Context analysis: {context}")

            # Step 2: Select appropriate format type and rules
            format_type = self.format_selector.select_format(context)
            format_rules = self.format_selector.get_format_rules(format_type)
            logger.info(f"Selected format: {format_type.value}, rules: {format_rules}")

            # Step 3: Generate raw content using Claude AI
            raw_response = await self._generate_with_model(
                user_input,
                context,
                format_rules
            )

            # Step 4: Apply post-processing formatting
            formatted_response = self.formatter.format_response(
                raw_response,
                format_rules
            )

            # Step 5: Quality check
            if self._quality_check(formatted_response):
                return {
                    'content': formatted_response,
                    'format_type': format_type.value,
                    'metadata': context,
                    'success': True
                }

            # Fallback if quality check fails
            logger.warning("Quality check failed, using fallback response")
            return self._generate_fallback(user_input)

        except Exception as e:
            logger.error(f"Error in generate_response: {e}", exc_info=True)
            return self._generate_fallback(user_input, error=str(e))

    async def _generate_with_model(
        self,
        user_input: str,
        context: Dict,
        format_rules: Dict
    ) -> str:
        """
        Generate raw AI response using Claude with context-aware system prompts.
        
        Args:
            user_input: The user's message.
            context: Context dictionary from ContextAnalyzer.
            format_rules: Formatting rules from FormatSelector.
            
        Returns:
            Raw AI-generated text.
        """
        # Build system prompt based on context and format rules
        system_prompt = self._build_system_prompt(context, format_rules)

        # Use Claude client to generate response
        if self.claude_client.is_enabled:
            raw_response = self.claude_client.generate_response(
                prompt=user_input,
                max_tokens=2048,
                temperature=0.7,
                system_prompt=system_prompt
            )
            return raw_response
        else:
            logger.warning("Claude AI is not enabled, returning placeholder")
            return "AI response generation is currently unavailable."

    def _build_system_prompt(self, context: Dict, format_rules: Dict) -> str:
        """
        Construct a system prompt tailored to the conversation context and format rules.
        
        Args:
            context: Analysis results from ContextAnalyzer.
            format_rules: Formatting preferences from FormatSelector.
            
        Returns:
            A system prompt string for the AI model.
        """
        base_prompt = "You are a helpful AI assistant."

        # Adjust tone based on context
        if context.get('is_casual'):
            base_prompt += " Keep your responses conversational and friendly."
        elif context.get('is_technical'):
            base_prompt += " Provide clear, technical explanations with examples where appropriate."
        elif context.get('is_emotional'):
            base_prompt += " Be empathetic and supportive in your responses."

        # Adjust structure based on format rules
        if format_rules.get('use_headers'):
            base_prompt += " Use markdown headers (## and ###) to organize your response."
        if format_rules.get('use_lists'):
            base_prompt += " Use bullet points or numbered lists for clarity."
        if format_rules.get('paragraph_style') == 'short':
            base_prompt += " Keep paragraphs brief and to the point."

        # Code-related guidance
        if context.get('needs_code'):
            base_prompt += " Include code examples wrapped in triple backticks with language identifiers (e.g., ```python)."

        return base_prompt

    def _quality_check(self, formatted_response: str) -> bool:
        """
        Perform basic quality checks on the formatted response.
        
        Args:
            formatted_response: The AI response after formatting.
            
        Returns:
            True if the response passes quality checks, False otherwise.
        """
        # Check minimum length
        if len(formatted_response.strip()) < 10:
            logger.warning("Response too short")
            return False

        # Check for placeholder or error messages
        error_indicators = [
            "error generating response",
            "ai is not configured",
            "response generation is currently unavailable"
        ]
        if any(indicator in formatted_response.lower() for indicator in error_indicators):
            logger.warning("Response contains error indicators")
            return False

        # Check for balanced code fences
        code_fence_count = formatted_response.count('```')
        if code_fence_count % 2 != 0:
            logger.warning("Unbalanced code fences detected")
            return False

        return True

    def _generate_fallback(self, user_input: str, error: Optional[str] = None) -> Dict:
        """
        Generate a fallback response when the main pipeline fails.
        
        Args:
            user_input: The user's original input.
            error: Optional error message to include in metadata.
            
        Returns:
            A dictionary with a generic fallback response.
        """
        fallback_content = (
            "I apologize, but I'm having trouble generating a response right now. "
            "Could you please try rephrasing your question or ask something else?"
        )
        
        return {
            'content': fallback_content,
            'format_type': FormatType.CONVERSATIONAL.value,
            'metadata': {'fallback': True, 'error': error},
            'success': False
        }
