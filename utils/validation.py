"""
Validation utilities for user input sanitization
"""
import re
from typing import Optional
from html import escape


class InputValidator:
    """Utility class for validating and sanitizing user inputs"""
    
    # Regex patterns
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{2,50}$')
    ROOM_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\s-]{2,100}$')
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Remove HTML tags and limit length"""
        if not text:
            return ""
        
        # Remove HTML tags
        sanitized = escape(text.strip())
        
        # Limit length
        return sanitized[:max_length]
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, Optional[str]]:
        """
        Validate username format
        Returns: (is_valid, error_message)
        """
        if not username:
            return False, "Username is required"
        
        if len(username) < 2:
            return False, "Username must be at least 2 characters"
        
        if len(username) > 50:
            return False, "Username must be at most 50 characters"
        
        if not InputValidator.USERNAME_PATTERN.match(username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_room_name(room_name: str) -> tuple[bool, Optional[str]]:
        """
        Validate room name format
        Returns: (is_valid, error_message)
        """
        if not room_name:
            return False, "Room name is required"
        
        if len(room_name) < 2:
            return False, "Room name must be at least 2 characters"
        
        if len(room_name) > 100:
            return False, "Room name must be at most 100 characters"
        
        if not InputValidator.ROOM_NAME_PATTERN.match(room_name):
            return False, "Room name can only contain letters, numbers, spaces, hyphens, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_message_content(content: str, max_length: int = 5000) -> tuple[bool, Optional[str]]:
        """
        Validate message content
        Returns: (is_valid, error_message)
        """
        if not content or not content.strip():
            return False, "Message cannot be empty"
        
        if len(content) > max_length:
            return False, f"Message must be at most {max_length} characters"
        
        return True, None
    
    @staticmethod
    def contains_spam_patterns(text: str) -> bool:
        """
        Check for common spam patterns
        """
        spam_patterns = [
            r'(https?://)?([a-z0-9-]+\.)+[a-z]{2,}(/\S*)?',  # URLs (excessive)
            r'(buy|click|discount|free|winner|congratulations)\s+(now|here)',  # Spam keywords
            r'(\w)\1{10,}',  # Repeated characters
        ]
        
        text_lower = text.lower()
        
        # Check URL frequency
        url_count = len(re.findall(spam_patterns[0], text))
        if url_count > 3:
            return True
        
        # Check spam keywords
        for pattern in spam_patterns[1:]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
