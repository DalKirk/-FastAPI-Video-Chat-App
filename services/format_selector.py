from enum import Enum
from typing import Dict

class FormatType(Enum):
    """Defines the different types of response formats."""
    CONVERSATIONAL = "conversational"
    STRUCTURED = "structured"
    CODE_FOCUSED = "code_focused"
    EMPATHETIC = "empathetic"
    BALANCED = "balanced"

class FormatSelector:
    """Selects an appropriate response format based on conversation context."""

    def select_format(self, context: Dict) -> FormatType:
        """
        Decision tree for selecting the best format type.
        
        Args:
            context: A dictionary of context flags from the ContextAnalyzer.
            
        Returns:
            The most appropriate FormatType for the response.
        """
        if context.get('is_technical') and context.get('needs_code'):
            return FormatType.CODE_FOCUSED
            
        if context.get('needs_structure'):
            return FormatType.STRUCTURED
            
        if context.get('is_emotional'):
            return FormatType.EMPATHETIC
            
        if context.get('is_casual') and not context.get('needs_structure'):
            return FormatType.CONVERSATIONAL
            
        return FormatType.BALANCED

    def get_format_rules(self, format_type: FormatType) -> Dict:
        """
        Returns a dictionary of formatting rules for the selected format type.
        
        Args:
            format_type: The FormatType enum member.
            
        Returns:
            A dictionary containing specific formatting guidelines.
        """
        rules = {
            FormatType.CONVERSATIONAL: {
                'use_headers': False,
                'use_lists': 'minimal',  # Use only for very simple enumerations
                'use_bold': 'minimal',   # For emphasis on single words
                'paragraph_style': 'short',
                'greeting': True,
                'sign_off': True,
            },
            FormatType.STRUCTURED: {
                'use_headers': True,
                'use_lists': True,       # Prefer numbered or bulleted lists
                'use_bold': 'moderate',  # For highlighting key terms or list items
                'paragraph_style': 'medium',
                'greeting': False,
                'sign_off': False,
            },
            FormatType.CODE_FOCUSED: {
                'use_headers': True,     # For separating explanation from code
                'use_lists': True,       # For steps or parameter descriptions
                'use_bold': 'moderate',  # For filenames, function names, etc.
                'paragraph_style': 'technical', # Clear and concise
                'greeting': False,
                'sign_off': False,
            },
            FormatType.EMPATHETIC: {
                'use_headers': False,
                'use_lists': False,
                'use_bold': 'minimal',
                'paragraph_style': 'short_and_reassuring',
                'greeting': True,
                'sign_off': True,
            },
            FormatType.BALANCED: {
                'use_headers': True,
                'use_lists': 'moderate', # Use lists where appropriate but don't force it
                'use_bold': 'moderate',
                'paragraph_style': 'medium',
                'greeting': False,
                'sign_off': False,
            }
        }
        return rules.get(format_type, rules[FormatType.BALANCED])
