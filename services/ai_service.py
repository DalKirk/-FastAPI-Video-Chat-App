from typing import Dict, List, Optional
from app.models.chat_models import Message
from services.context_analyzer import ContextAnalyzer
from services.format_selector import FormatSelector, FormatType
from services.response_formatter import ResponseFormatter
from utils.claude_client import get_claude_client
import logging
import re

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

            # Step 3: Generate raw content using Claude AI with markdown guidance
            raw_response = await self._generate_with_model(
                user_input,
                context,
                format_rules
            )

            # Step 4: Convert plain text to proper markdown if needed
            markdown_response = self._ensure_markdown_format(raw_response, context, format_rules)

            # Step 5: Apply post-processing formatting (cleanup, not restructure)
            formatted_response = self.formatter.format_response(
                markdown_response,
                format_rules
            )

            # Step 6: Quality check
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
        Generate raw AI response using Claude with explicit markdown instructions.
        """
        # Build system prompt with explicit markdown formatting instructions
        system_prompt = self._build_markdown_system_prompt(context, format_rules)

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

    def _build_markdown_system_prompt(self, context: Dict, format_rules: Dict) -> str:
        """
        Construct a system prompt that explicitly requests markdown formatting.
        """
        base_prompt = "You are a helpful AI assistant. "
        
        # Add explicit markdown instructions
        markdown_instructions = (
            "Format your responses using proper markdown syntax:\n"
            "- Use ## for main section headers and ### for subsections\n"
            "- Use - or * for bullet points (one per line)\n"
            "- Use 1., 2., 3. for numbered lists\n"
            "- Use **bold** for emphasis on important terms\n"
            "- Use `inline code` for short code snippets\n"
            "- Use ```language blocks for multi-line code\n"
            "- Add blank lines between sections for readability\n\n"
        )
        
        base_prompt += markdown_instructions

        # Adjust tone and structure based on context
        if context.get('is_casual'):
            base_prompt += "Keep your tone conversational and friendly. Use short paragraphs.\n"
        elif context.get('is_technical'):
            base_prompt += "Provide clear, technical explanations. Use headers to organize sections.\n"
        elif context.get('is_emotional'):
            base_prompt += "Be empathetic and supportive. Use a warm, reassuring tone.\n"

        # Format-specific instructions
        if format_rules.get('use_headers'):
            base_prompt += "Organize your response with clear headers (## Header).\n"
        if format_rules.get('use_lists'):
            base_prompt += "Use bullet points or numbered lists to make information scannable.\n"
        if format_rules.get('paragraph_style') == 'short':
            base_prompt += "Keep paragraphs brief (2-3 sentences max).\n"

        # Code-related guidance
        if context.get('needs_code'):
            base_prompt += (
                "Include code examples wrapped in triple backticks with language identifiers.\n"
                "Example:\n```python\ndef example():\n    pass\n```\n"
            )

        return base_prompt

    def _ensure_markdown_format(self, content: str, context: Dict, format_rules: Dict) -> str:
        """
        Convert plain text to proper markdown if the AI didn't format it correctly.
        This acts as a safety net to ensure markdown structure.
        """
        # If content already has markdown, return as-is
        if self._has_markdown_structure(content):
            return content

        # Otherwise, intelligently convert to markdown
        lines = content.split('\n')
        formatted_lines = []
        in_code_block = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                formatted_lines.append('')
                continue

            # Detect code blocks
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                formatted_lines.append(line)
                continue

            if in_code_block:
                formatted_lines.append(line)
                continue

            # Convert numbered patterns to markdown lists
            # Match: "1.", "First,", "Second,", etc.
            numbered_pattern = r'^(\d+\.|\d+\))\s*(.+)$'
            word_number_pattern = r'^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth)[,:]?\s*(.+)$'

            numbered_match = re.match(numbered_pattern, stripped)
            word_match = re.match(word_number_pattern, stripped, re.IGNORECASE)

            if numbered_match:
                content_part = numbered_match.group(2)
                formatted_lines.append(f"- {content_part}")
            elif word_match:
                word = word_match.group(1)
                content_part = word_match.group(2)
                formatted_lines.append(f"- **{word}**: {content_part}")
            # Detect potential headers (short, title-case, no ending punctuation)
            elif (len(stripped) < 60 and 
                  stripped[0].isupper() and 
                  not stripped.endswith(('.', '!', '?', ',')) and
                  format_rules.get('use_headers')):
                # Check if next line exists and is content
                if i + 1 < len(lines) and lines[i + 1].strip():
                    formatted_lines.append(f"## {stripped}")
                else:
                    formatted_lines.append(stripped)
            # Already a list item (-, *, •)
            elif stripped.startswith(('-', '*', '•')):
                clean_content = stripped.lstrip('-*• ').strip()
                formatted_lines.append(f"- {clean_content}")
            else:
                # Regular paragraph
                formatted_lines.append(stripped)

        # Join and clean up excessive blank lines
        result = '\n'.join(formatted_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)
        return result.strip()

    def _has_markdown_structure(self, content: str) -> bool:
        """Check if content already has markdown formatting."""
        markdown_indicators = [
            r'^#+\s',           # Headers
            r'^\s*[-*]\s',      # Bullet lists
            r'^\s*\d+\.\s',     # Numbered lists
            r'\*\*\w+\*\*',     # Bold
            r'`\w+`',           # Inline code
            r'```',             # Code blocks
        ]
        for pattern in markdown_indicators:
            if re.search(pattern, content, re.MULTILINE):
                return True
        return False

    def _quality_check(self, formatted_response: str) -> bool:
        """
        Perform basic quality checks on the formatted response.
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
