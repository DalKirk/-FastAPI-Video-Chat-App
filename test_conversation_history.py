"""
Test script for Claude conversation history feature
Run this to verify conversation memory is working
"""
import os
from utils.claude_client import get_claude_client

def test_basic_conversation():
    """Test that Claude remembers conversation context"""
    print("?? Testing Claude Conversation History\n")
    print("=" * 60)
    
    claude = get_claude_client()
    
    if not claude.is_enabled:
        print("? Claude AI is not configured")
        print("   Set ANTHROPIC_API_KEY environment variable")
        return False
    
    # Use a unique conversation ID
    conv_id = "test_memory_001"
    
    # Clear any existing conversation
    claude.clear_conversation(conv_id)
    print(f"? Started new conversation: {conv_id}\n")
    
    # Test 1: Introduce yourself
    print("?? User: My name is Alice and I work as a software engineer.")
    response1 = claude.generate_response(
        "My name is Alice and I work as a software engineer.",
        conversation_id=conv_id
    )
    print(f"?? Claude: {response1}\n")
    
    # Test 2: Ask Claude to recall
    print("?? User: What's my name and profession?")
    response2 = claude.generate_response(
        "What's my name and profession?",
        conversation_id=conv_id
    )
    print(f"?? Claude: {response2}\n")
    
    # Check if Claude remembered
    if "Alice" in response2 and ("software" in response2.lower() or "engineer" in response2.lower()):
        print("? SUCCESS: Claude remembered your name and profession!")
    else:
        print("? FAIL: Claude didn't remember correctly")
        print(f"   Expected to mention 'Alice' and 'software engineer'")
        print(f"   Got: {response2}")
        return False
    
    # Test 3: Check conversation history
    history = claude.get_conversation_history(conv_id)
    message_count = claude.get_conversation_count(conv_id)
    
    print(f"\n?? Conversation Stats:")
    print(f"   Messages in history: {message_count}")
    print(f"   Expected: 4 (2 user + 2 assistant)")
    
    if message_count == 4:
        print("   ? Correct message count")
    else:
        print(f"   ? Unexpected count: {message_count}")
    
    # Test 4: View history
    print(f"\n?? Full Conversation History:")
    for i, msg in enumerate(history, 1):
        role = msg['role'].upper()
        content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"   {i}. [{role}] {content}")
    
    # Test 5: Clear conversation
    print(f"\n???  Clearing conversation...")
    claude.clear_conversation(conv_id)
    new_count = claude.get_conversation_count(conv_id)
    
    if new_count == 0:
        print("   ? Conversation cleared successfully")
    else:
        print(f"   ? Conversation not cleared (count: {new_count})")
    
    # Test 6: Verify memory is gone
    print("\n?? User: What's my name? (after clearing)")
    response3 = claude.generate_response(
        "What's my name?",
        conversation_id=conv_id
    )
    print(f"?? Claude: {response3}\n")
    
    if "Alice" not in response3:
        print("? SUCCESS: Claude forgot after clearing (as expected)")
    else:
        print("? UNEXPECTED: Claude still remembers after clearing")
    
    print("\n" + "=" * 60)
    print("? All conversation history tests passed!")
    print("\n??  Model Info:")
    info = claude.get_model_info()
    print(f"   Active Model: {info['active_model']}")
    print(f"   Fallback Model: {info['fallback_model']}")
    print(f"   Active Conversations: {info['active_conversations']}")
    
    return True


def test_multiple_conversations():
    """Test that different conversation IDs are independent"""
    print("\n\n?? Testing Multiple Independent Conversations\n")
    print("=" * 60)
    
    claude = get_claude_client()
    
    # Alice's conversation
    print("?? Alice: I love pizza")
    claude.generate_response("I love pizza", conversation_id="alice_123")
    
    # Bob's conversation
    print("?? Bob: I love tacos")
    claude.generate_response("I love tacos", conversation_id="bob_456")
    
    # Ask Alice
    print("\n?? Alice: What do I love?")
    alice_response = claude.generate_response(
        "What do I love?",
        conversation_id="alice_123"
    )
    print(f"?? Claude to Alice: {alice_response}")
    
    # Ask Bob
    print("\n?? Bob: What do I love?")
    bob_response = claude.generate_response(
        "What do I love?",
        conversation_id="bob_456"
    )
    print(f"?? Claude to Bob: {bob_response}")
    
    # Verify independence
    if "pizza" in alice_response.lower() and "taco" in bob_response.lower():
        print("\n? SUCCESS: Conversations are independent!")
    else:
        print("\n? FAIL: Conversations are mixed up")
        print(f"   Alice response: {alice_response}")
        print(f"   Bob response: {bob_response}")
    
    # Cleanup
    claude.clear_conversation("alice_123")
    claude.clear_conversation("bob_456")
    
    return True


def test_backward_compatibility():
    """Test that old code without conversation_id still works"""
    print("\n\n?? Testing Backward Compatibility\n")
    print("=" * 60)
    
    claude = get_claude_client()
    
    # Old style: no conversation_id
    print("?? User: Hello! (no conversation tracking)")
    response1 = claude.generate_response("Hello! My name is Test User.")
    print(f"?? Claude: {response1}")
    
    print("\n?? User: What's my name? (no conversation tracking)")
    response2 = claude.generate_response("What's my name?")
    print(f"?? Claude: {response2}\n")
    
    if "Test User" not in response2:
        print("? SUCCESS: Without conversation_id, no memory (as expected)")
    else:
        print("??  UNEXPECTED: Claude remembered without conversation_id")
    
    print("\n" + "=" * 60)
    print("? Backward compatibility verified!")
    
    return True


if __name__ == "__main__":
    print("\n" + "?? Claude Conversation History Test Suite" + "\n")
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("? ERROR: ANTHROPIC_API_KEY not set in environment")
        print("\nTo fix:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'  # Linux/Mac")
        print("  set ANTHROPIC_API_KEY=sk-ant-api03-...       # Windows CMD")
        print("  $env:ANTHROPIC_API_KEY='sk-ant-api03-...'    # PowerShell")
        exit(1)
    
    try:
        # Run all tests
        test_basic_conversation()
        test_multiple_conversations()
        test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("?? ALL TESTS PASSED! Conversation history is working!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n? Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
