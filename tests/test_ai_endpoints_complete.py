"""
Comprehensive test for AI Endpoints with Web Search Integration
Tests all endpoints including the new web search functionality
"""
import os
import asyncio
import json
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API keys are available
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
BRAVE_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

# Skip all tests if ANTHROPIC_API_KEY is not set
pytestmark = pytest.mark.skipif(
    not ANTHROPIC_KEY,
    reason="ANTHROPIC_API_KEY not set in environment"
)

print("=" * 70)
print("?? AI ENDPOINTS COMPREHENSIVE TEST")
print("=" * 70)

# Check API key status
print("\n?? API Key Status:")
print(f"   ANTHROPIC_API_KEY: {'? SET' if ANTHROPIC_KEY else '? NOT SET'}")
print(f"   BRAVE_SEARCH_API_KEY: {'? SET' if BRAVE_KEY else '? NOT SET'}")

if not ANTHROPIC_KEY:
    print("\n? ANTHROPIC_API_KEY not found - tests will be skipped")
    print("   Add it to your .env file to run these tests.")

# Import after checking keys
try:
    from main import app
    client = TestClient(app)
except ImportError:
    # If main.py doesn't exist, skip tests
    pytest.skip("main.py not found", allow_module_level=True)


def test_health_check():
    """Test AI health check endpoint"""
    print("\n" + "=" * 70)
    print("Test 1: Health Check (/ai/health)")
    print("=" * 70)
    
    response = client.get("/ai/health")
    print(f"\n?? Status Code: {response.status_code}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    print(f"? AI Enabled: {data.get('ai_enabled')}")
    print(f"? Search Enabled: {data.get('search_enabled')}")
    print(f"? Model: {data.get('model')}")
    print(f"? Active Conversations: {data.get('active_conversations')}")
    print(f"? Features: {', '.join(data.get('features', []))}")
    
    # Verify web_search is in features
    assert 'web_search' in data.get('features', []), "web_search feature not found"
    print("? Web search feature detected!")


def test_generate_without_search():
    """Test AI generation without web search"""
    print("\n" + "=" * 70)
    print("Test 2: Generate Response (No Search)")
    print("=" * 70)
    
    payload = {
        "prompt": "Explain what Python is in one sentence",
        "max_tokens": 100,
        "temperature": 0.7,
        "enable_search": False
    }
    
    print(f"\n?? Request: {json.dumps(payload, indent=2)}")
    
    response = client.post("/ai/generate", json=payload)
    print(f"\n?? Status Code: {response.status_code}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'response' in data, "Response field missing"
    assert len(data.get('response', '')) > 0, "Empty response"
    
    print(f"? Response Length: {data.get('debug_info', {}).get('response_length')} characters")
    print(f"? Model: {data.get('model')}")
    print(f"? Search Enabled: {data.get('search_enabled')}")
    print(f"\n?? Response Preview:")
    print(f"   {data.get('response', '')[:150]}...")


@pytest.mark.skipif(not BRAVE_KEY, reason="BRAVE_SEARCH_API_KEY not set")
def test_generate_with_search():
    """Test AI generation with web search"""
    print("\n" + "=" * 70)
    print("Test 3: Generate Response (With Search)")
    print("=" * 70)
    
    payload = {
        "prompt": "What are the latest developments in AI technology?",
        "max_tokens": 300,
        "temperature": 0.7,
        "enable_search": True
    }
    
    print(f"\n?? Request: {json.dumps(payload, indent=2)}")
    
    response = client.post("/ai/generate", json=payload)
    print(f"\n?? Status Code: {response.status_code}")
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.json()
    assert 'response' in data, "Response field missing"
    
    print(f"? Response Length: {data.get('debug_info', {}).get('response_length')} characters")
    print(f"? Model: {data.get('model')}")
    print(f"? Search Enabled: {data.get('search_enabled')}")
    
    response_text = data.get('response', '')
    print(f"\n?? Response Preview:")
    print(f"   {response_text[:200]}...")
    
    # Check for source citations
    has_sources = any(word in response_text.lower() for word in ['source', 'according', 'url', 'http'])
    if has_sources:
        print("\n? Response includes source citations!")


def test_conversation_history():
    """Test conversation history with web search"""
    print("\n" + "=" * 70)
    print("Test 4: Conversation History + Search")
    print("=" * 70)
    
    conversation_id = "test_conv_search_001"
    
    # First message
    print("\n?? Message 1: Setting context...")
    payload1 = {
        "prompt": "My favorite programming language is Python",
        "conversation_id": conversation_id,
        "max_tokens": 100,
        "enable_search": False
    }
    
    response1 = client.post("/ai/generate", json=payload1)
    assert response1.status_code == 200
    
    data1 = response1.json()
    print(f"? Sent: {payload1['prompt']}")
    print(f"? Conversation Length: {data1.get('conversation_length')}")
    
    # Second message - test memory
    print("\n?? Message 2: Testing memory...")
    payload2 = {
        "prompt": "What's my favorite language?",
        "conversation_id": conversation_id,
        "max_tokens": 100,
        "enable_search": False
    }
    
    response2 = client.post("/ai/generate", json=payload2)
    assert response2.status_code == 200
    
    data2 = response2.json()
    response_text = data2.get('response', '').lower()
    print(f"? Response: {data2.get('response')}")
    print(f"? Conversation Length: {data2.get('conversation_length')}")
    
    assert 'python' in response_text, "Claude did not remember the conversation"
    print("? Claude remembered the conversation!")
    
    # Third message - search with history (only if Brave key available)
    if BRAVE_KEY:
        print("\n?? Message 3: Search query with context...")
        payload3 = {
            "prompt": "What are the latest updates for my favorite language?",
            "conversation_id": conversation_id,
            "max_tokens": 200,
            "enable_search": True
        }
        
        response3 = client.post("/ai/generate", json=payload3)
        assert response3.status_code == 200
        
        data3 = response3.json()
        print(f"? Response Length: {len(data3.get('response', ''))}")
        print(f"? Conversation Length: {data3.get('conversation_length')}")
        print(f"? Search Enabled: {data3.get('search_enabled')}")
        print(f"\n?? Response Preview:")
        print(f"   {data3.get('response', '')[:200]}...")
    
    # Clean up
    print("\n?? Cleaning up conversation...")
    cleanup = client.post("/ai/conversation/clear", json={"conversation_id": conversation_id})
    assert cleanup.status_code == 200
    print("? Conversation cleared")


def test_content_moderation():
    """Test content moderation"""
    print("\n" + "=" * 70)
    print("Test 5: Content Moderation")
    print("=" * 70)
    
    payload = {
        "content": "This is a friendly test message"
    }
    
    response = client.post("/ai/moderate", json=payload)
    print(f"\n?? Status Code: {response.status_code}")
    
    assert response.status_code == 200
    
    data = response.json()
    assert 'is_safe' in data, "is_safe field missing"
    
    print(f"? Is Safe: {data.get('is_safe')}")
    print(f"? Reason: {data.get('reason')}")
    print(f"? Confidence: {data.get('confidence')}")


def test_conversation_endpoints():
    """Test conversation management endpoints"""
    print("\n" + "=" * 70)
    print("Test 6: Conversation Management")
    print("=" * 70)
    
    conv_id = "test_mgmt_001"
    
    # Create some history
    print("\n?? Creating conversation...")
    for i in range(3):
        payload = {
            "prompt": f"Message {i+1}",
            "conversation_id": conv_id,
            "max_tokens": 50,
            "enable_search": False
        }
        response = client.post("/ai/generate", json=payload)
        assert response.status_code == 200
    
    # Get count
    print("\n?? Getting conversation count...")
    count_response = client.get(f"/ai/conversation/{conv_id}/count")
    assert count_response.status_code == 200
    
    data = count_response.json()
    assert data.get('message_count', 0) > 0
    print(f"? Message Count: {data.get('message_count')}")
    
    # Get history
    print("\n?? Getting conversation history...")
    history_response = client.get(f"/ai/conversation/{conv_id}/history")
    assert history_response.status_code == 200
    
    data = history_response.json()
    print(f"? Retrieved {data.get('message_count')} messages")
    
    # Clear
    print("\n?? Clearing conversation...")
    clear_response = client.post("/ai/conversation/clear", json={"conversation_id": conv_id})
    assert clear_response.status_code == 200
    print("? Conversation cleared successfully")


if __name__ == "__main__":
    # Run with pytest
    pytest.main([__file__, "-v"])
