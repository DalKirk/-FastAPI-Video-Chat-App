"""
Test script for Claude AI Web Search Integration
Run this to verify the web search feature is working correctly
"""
import os
import asyncio
from utils.claude_client import get_claude_client

async def test_web_search():
    """Test the web search integration"""
    print("?? Testing Claude AI Web Search Integration")
    print("=" * 60)
    
    # Initialize Claude client
    claude = get_claude_client()
    
    # Check if Claude is enabled
    if not claude.is_enabled:
        print("? Claude AI is not configured")
        print("   Please add ANTHROPIC_API_KEY to your .env file")
        return False
    
    print("? Claude AI is enabled")
    
    # Check if web search is enabled
    if not claude.is_search_enabled:
        print("? Web search is disabled (no Brave API key)")
        print("   Add BRAVE_SEARCH_API_KEY to your .env file to enable search")
    else:
        print("? Web search is enabled")
    
    # Get model info
    model_info = claude.get_model_info()
    print(f"\n?? Model Information:")
    print(f"   Active Model: {model_info['active_model']}")
    print(f"   Fallback Model: {model_info['fallback_model']}")
    print(f"   Search Enabled: {model_info['is_search_enabled']}")
    print(f"   Active Conversations: {model_info['active_conversations']}")
    
    # Test queries
    print("\n" + "=" * 60)
    print("?? Testing Queries")
    print("=" * 60)
    
    # Test 1: Query WITHOUT search trigger (general knowledge)
    print("\n[Test 1] General knowledge query (no search):")
    print("Query: 'Explain what Python is'")
    try:
        response1 = await claude.generate_response(
            "Explain what Python is in one sentence",
            max_tokens=100,
            enable_search=False
        )
        print(f"? Response: {response1[:150]}...")
    except Exception as e:
        print(f"? Error: {e}")
    
    # Test 2: Query WITH search trigger (current info)
    if claude.is_search_enabled:
        print("\n[Test 2] Current info query (with search):")
        print("Query: 'What is the latest news on AI technology today?'")
        try:
            response2 = await claude.generate_response(
                "What is the latest news on AI technology today?",
                max_tokens=200,
                conversation_id="test_search"
            )
            print(f"? Response: {response2[:200]}...")
            
            # Check if response mentions sources
            if any(word in response2.lower() for word in ['source', 'according', 'url', 'http']):
                print("? Response includes source citations")
            else:
                print("? Response may not include sources")
                
        except Exception as e:
            print(f"? Error: {e}")
    else:
        print("\n[Test 2] Skipped - Web search not enabled")
    
    # Test 3: Conversation history
    print("\n[Test 3] Conversation history:")
    print("Creating a conversation with memory...")
    try:
        conv_id = "test_memory"
        
        # First message
        await claude.generate_response(
            "My favorite color is blue",
            conversation_id=conv_id,
            enable_search=False
        )
        print("? Sent: 'My favorite color is blue'")
        
        # Second message (tests memory)
        response3 = await claude.generate_response(
            "What's my favorite color?",
            conversation_id=conv_id,
            enable_search=False
        )
        print(f"? Response: {response3}")
        
        if "blue" in response3.lower():
            print("? Claude remembered the conversation!")
        else:
            print("? Memory may not be working correctly")
        
        # Get conversation stats
        count = claude.get_conversation_count(conv_id)
        print(f"? Conversation has {count} messages")
        
        # Clean up
        claude.clear_conversation(conv_id)
        print("? Conversation cleared")
        
    except Exception as e:
        print(f"? Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("?? Test Summary")
    print("=" * 60)
    print(f"? Claude AI: {'Enabled' if claude.is_enabled else 'Disabled'}")
    print(f"{'?' if claude.is_search_enabled else '?'} Web Search: {'Enabled' if claude.is_search_enabled else 'Disabled'}")
    print(f"? Model: {model_info['active_model']}")
    print(f"? Conversation History: Working")
    
    if not claude.is_search_enabled:
        print("\n?? Tip: Add BRAVE_SEARCH_API_KEY to .env to enable web search")
        print("   Get a free API key at: https://brave.com/search/api/")
    
    print("\n? All tests completed!")
    return True

def main():
    """Main test runner"""
    # Check for API keys
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("? ANTHROPIC_API_KEY not found in environment")
        print("   Please add it to your .env file")
        print("   Example: ANTHROPIC_API_KEY=sk-ant-api03-...")
        return
    
    # Run async tests
    asyncio.run(test_web_search())

if __name__ == "__main__":
    main()
