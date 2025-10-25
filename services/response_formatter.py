import re
from typing import Dict, List

class ResponseFormatter:
    """Applies markdown formatting to AI responses based on a set of rules."""

    def format_response(self, raw_content: str, format_rules: Dict) -> str:
        """
        Apply a series of formatting rules to the raw text content.
        The order of operations is important to avoid conflicting rules.
        """
        # Isolate code blocks to prevent them from being altered by other formatters.
        parts = re.split(r"(```.*?```)", raw_content, flags=re.DOTALL)
        formatted_parts = []

        for i, part in enumerate(parts):
            # If the part is a code block (odd indices), append it without changes.
            if i % 2 == 1:
                formatted_parts.append(part)
                continue

            # Otherwise, apply formatting rules to the non-code part.
            formatted_part = part
            
            if format_rules.get('use_headers'):
                formatted_part = self._enhance_headers(formatted_part)
            
            if format_rules.get('use_lists'):
                formatted_part = self._format_lists(formatted_part)
            
            if format_rules.get('use_bold') == 'moderate':
                # Emphasize keywords in non-code text
                formatted_part = self._emphasize_keywords(
                    formatted_part, 
                    ['important', 'note', 'warning', 'error', 'success']
                )

            formatted_parts.append(formatted_part)

        return "".join(formatted_parts)

    def _enhance_headers(self, content: str) -> str:
        """
        Ensures proper markdown header hierarchy.
        This heuristic converts short, title-cased lines ending with a colon into headers.
        """
        lines = content.split('\n')
        formatted_lines = []
        for line in lines:
            stripped_line = line.strip()
            # Check if the line is short, ends with ':', and is mostly title-cased.
            if 1 < len(stripped_line) < 60 and stripped_line.endswith(':'):
                header_candidate = stripped_line[:-1]
                if header_candidate.istitle() or header_candidate.isupper():
                    # Use ### for indented lines, ## for others.
                    if line.startswith('  ') or line.startswith('\t'):
                        formatted_lines.append(f"### {header_candidate}")
                    else:
                        formatted_lines.append(f"## {header_candidate}")
                    continue
            formatted_lines.append(line)
        return '\n'.join(formatted_lines)

    def _format_lists(self, content: str) -> str:
        """
        Formats bullet points and numbered lists for consistency.
        Ensures there is a space after the list marker.
        """
        # For bulleted lists (* or -)
        content = re.sub(r"^\s*([*-])\s*(\S)", r"\1 \2", content, flags=re.MULTILINE)
        # For numbered lists (1., 2., etc.)
        content = re.sub(r"^\s*(\d+\.)\s*(\S)", r"\1 \2", content, flags=re.MULTILINE)
        return content

    def _emphasize_keywords(self, content: str, keywords: List[str]) -> str:
        """
        Wraps specific keywords in bold markdown (`**keyword**`) for emphasis.
        Uses word boundaries to avoid matching substrings inside other words.
        """
        for keyword in keywords:
            # \b ensures we match whole words only.
            # re.IGNORECASE makes the match case-insensitive.
            content = re.sub(r"\b(" + re.escape(keyword) + r")\b", r"**\1**", content, flags=re.IGNORECASE)
        return content
