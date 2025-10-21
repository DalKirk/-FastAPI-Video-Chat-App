"""
Test script for the Anthropic Claude SDK integration
"""
import os
from utils.claude_client import get_claude_client

def test_claude_agent():
    """Test basic Claude SDK functionality"""
    print("Testing Anthropic Claude SDK integration...")
    
    # Get the Claude client
    claude = get_claude_client()
    
    if not claude.is_enabled:
        print("Claude AI is not configured. Add ANTHROPIC_API_KEY to environment.")
        return
    
    # Test generating a response
    print("\nGenerating a response...")
    response = claude.generate_response("Hello! Can you tell me a fun fact about space?")
    print(f"Response: {response}")
    
    # Test content moderation
    print("\nTesting content moderation...")
    moderation = claude.moderate_content("This is a test message, please moderate it.")
    print(f"Moderation: {moderation}")
    
    print("\nTests completed!")

if __name__ == "__main__":
    test_claude_agent()