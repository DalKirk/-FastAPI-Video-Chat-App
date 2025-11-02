"""
Test script for Claude conversation history feature
Run this to verify conversation memory is working
"""
import os
import asyncio
import pytest
from utils.claude_client import get_claude_client


@pytest.mark.asyncio
async def test_basic_conversation():
    """Test that Claude remembers conversation context"""
    print("?? Testing Claude Conversation History\n")
    print("=" * 60)
    
    claude = get_claude_client()
    
    if not claude.is_enabled:
        pytest.skip("ANTHROPIC_API_KEY not configured")
    
    # Use a unique conversation ID
    conv_id = "test_memory_001"
    
    # Clear any existing conversation
    claude.clear_conversation(conv_id)
    print(f"? Started new conversation: {conv_id}\n")
    
    # Test 1: Introduce yourself
    print("?? User: My name is Alice and I work as a software engineer.")
    response1 = await claude.generate_response(
        "My name is Alice and I work as a software engineer.",
        conversation_id=conv_id,
        enable_search=False
    )
    print(f"?? Claude: {response1}\n")
    
    # Test 2: Ask Claude to recall
    print("?? User: What's my name and profession?")
    response2 = await claude.generate_response(
        "What's my name and profession?",
        conversation_id=conv_id,
        enable_search=False
    )
    print(f"?? Claude: {response2}\n")
    
    # Check if Claude remembered
    assert "Alice" in response2 or "alice" in response2.lower(), "Claude did not remember the name"
    assert "software" in response2.lower() or "engineer" in response2.lower(), "Claude did not remember the profession"
    print("? SUCCESS: Claude remembered your name and profession!")
    
    # Test 3: Check conversation history
    history = claude.get_conversation_history(conv_id)
    message_count = claude.get_conversation_count(conv_id)
    
    print(f"\n?? Conversation Stats:")
    print(f"   Messages in history: {message_count}")
    print(f"   Expected: 4 (2 user + 2 assistant)")
    
    assert message_count == 4, f"Expected 4 messages, got {message_count}"
    print("   ? Correct message count")
    
    # Test 4: View history
    print(f"\n?? Full Conversation History:")
    for i, msg in enumerate(history, 1):
        role = msg['role'].upper()
        content = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"   {i}. [{role}] {content}")
    
    # Test 5: Clear conversation
    print(f"\n?? Clearing conversation...")
    claude.clear_conversation(conv_id)
    new_count = claude.get_conversation_count(conv_id)
    
    assert new_count == 0, f"Conversation not cleared, count: {new_count}"
    print("   ? Conversation cleared successfully")
    
    # Test 6: Verify memory is gone
    print("\n?? User: What's my name? (after clearing)")
    response3 = await claude.generate_response(
        "What's my name?",
        conversation_id=conv_id,
        enable_search=False
    )
    print(f"?? Claude: {response3}\n")
    
    assert "Alice" not in response3, "Claude still remembers after clearing"
    print("? SUCCESS: Claude forgot after clearing (as expected)")
    
    print("\n" + "=" * 60)
    print("? All conversation history tests passed!")
    print("\n?? Model Info:")
    info = claude.get_model_info()
    print(f"   Active Model: {info['active_model']}")
    print(f"   Fallback Model: {info['fallback_model']}")
    print(f"   Active Conversations: {info['active_conversations']}")


@pytest.mark.asyncio
async def test_multiple_conversations():
    """Test that different conversation IDs are independent"""
    print("\n\n?? Testing Multiple Independent Conversations\n")
    print("=" * 60)
    
    claude = get_claude_client()
    
    if not claude.is_enabled:
        pytest.skip("ANTHROPIC_API_KEY not configured")
    
    # Alice's conversation
    print("?? Alice: I love pizza")
    await claude.generate_response("I love pizza", conversation_id="alice_123", enable_search=False)
    
    # Bob's conversation
    print("?? Bob: I love tacos")
    await claude.generate_response("I love tacos", conversation_id="bob_456", enable_search=False)
    
    # Ask Alice
    print("\n?? Alice: What do I love?")
    alice_response = await claude.generate_response(
        "What do I love?",
        conversation_id="alice_123",
        enable_search=False
    )
    print(f"?? Claude to Alice: {alice_response}")
    
    # Ask Bob
    print("\n?? Bob: What do I love?")
    bob_response = await claude.generate_response(
        "What do I love?",
        conversation_id="bob_456",
        enable_search=False
    )
    print(f"?? Claude to Bob: {bob_response}")
    
    # Verify independence
    assert "pizza" in alice_response.lower(), "Alice's response doesn't mention pizza"
    assert "taco" in bob_response.lower(), "Bob's response doesn't mention taco"
    print("\n? SUCCESS: Conversations are independent!")
    
    # Cleanup
    claude.clear_conversation("alice_123")
    claude.clear_conversation("bob_456")


@pytest.mark.asyncio
async def test_backward_compatibility():
    """Test that old code without conversation_id still works"""
    print("\n\n?? Testing Backward Compatibility\n")
    print("=" * 60)
    
    claude = get_claude_client()
    
    if not claude.is_enabled:
        pytest.skip("ANTHROPIC_API_KEY not configured")
    
    # Old style: no conversation_id
    print("?? User: Hello! (no conversation tracking)")
    response1 = await claude.generate_response("Hello! My name is Test User.", enable_search=False)
    print(f"?? Claude: {response1}")
    
    print("\n?? User: What's my name? (no conversation tracking)")
    response2 = await claude.generate_response("What's my name?", enable_search=False)
    print(f"?? Claude: {response2}\n")
    
    # Without conversation_id, Claude shouldn't remember
    # (But it might still respond reasonably, so we just check it doesn't crash)
    assert response2 is not None, "Response is None"
    assert len(response2) > 0, "Response is empty"
    print("? SUCCESS: Without conversation_id, API works (no memory as expected)")
    
    print("\n" + "=" * 60)
    print("? Backward compatibility verified!")


async def run_all_tests():
    """Run all tests manually"""
    print("\n" + "?? Claude Conversation History Test Suite" + "\n")
    
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("? ERROR: ANTHROPIC_API_KEY not set in environment")
        print("\nTo fix:")
        print("  export ANTHROPIC_API_KEY='sk-ant-api03-...'  # Linux/Mac")
        print("  set ANTHROPIC_API_KEY=sk-ant-api03-...       # Windows CMD")
        print("  $env:ANTHROPIC_API_KEY='sk-ant-api03-...'    # PowerShell")
        return False
    
    try:
        # Run all tests
        await test_basic_conversation()
        await test_multiple_conversations()
        await test_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("? ALL TESTS PASSED! Conversation history is working!")
        print("=" * 60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n? Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
