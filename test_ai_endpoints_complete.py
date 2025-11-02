"""
Comprehensive test for AI Endpoints with Web Search Integration
Tests all endpoints including the new web search functionality
"""
import os
import asyncio
import json
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API keys are available
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
BRAVE_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

print("=" * 70)
print("?? AI ENDPOINTS COMPREHENSIVE TEST")
print("=" * 70)

# Check API key status
print("\n?? API Key Status:")
print(f"   ANTHROPIC_API_KEY: {'? SET' if ANTHROPIC_KEY else '? NOT SET'}")
print(f"   BRAVE_SEARCH_API_KEY: {'? SET' if BRAVE_KEY else '? NOT SET'}")

if not ANTHROPIC_KEY:
    print("\n? ERROR: ANTHROPIC_API_KEY not found!")
    print("   Please add it to your .env file to run these tests.")
    exit(1)

# Import after checking keys
from main import app

client = TestClient(app)

def test_health_check():
    """Test AI health check endpoint"""
    print("\n" + "=" * 70)
    print("Test 1: Health Check (/ai/health)")
    print("=" * 70)
    
    response = client.get("/ai/health")
    print(f"\n?? Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"? AI Enabled: {data.get('ai_enabled')}")
        print(f"? Search Enabled: {data.get('search_enabled')}")
        print(f"? Model: {data.get('model')}")
        print(f"? Active Conversations: {data.get('active_conversations')}")
        print(f"? Features: {', '.join(data.get('features', []))}")
        
        # Verify web_search is in features
        if 'web_search' in data.get('features', []):
            print("? Web search feature detected!")
        else:
            print("? Web search feature NOT in features list")
        
        return True
    else:
        print(f"? Failed: {response.text}")
        return False

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
    
    if response.status_code == 200:
        data = response.json()
        print(f"? Response Length: {data.get('debug_info', {}).get('response_length')} characters")
        print(f"? Model: {data.get('model')}")
        print(f"? Search Enabled: {data.get('search_enabled')}")
        print(f"\n?? Response Preview:")
        print(f"   {data.get('response', '')[:150]}...")
        return True
    else:
        print(f"? Failed: {response.text}")
        return False

def test_generate_with_search():
    """Test AI generation with web search"""
    print("\n" + "=" * 70)
    print("Test 3: Generate Response (With Search)")
    print("=" * 70)
    
    if not BRAVE_KEY:
        print("? Skipping: BRAVE_SEARCH_API_KEY not set")
        return None
    
    payload = {
        "prompt": "What are the latest developments in AI technology?",
        "max_tokens": 300,
        "temperature": 0.7,
        "enable_search": True
    }
    
    print(f"\n?? Request: {json.dumps(payload, indent=2)}")
    
    response = client.post("/ai/generate", json=payload)
    print(f"\n?? Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
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
        else:
            print("\n? Response may not include sources")
        
        return True
    else:
        print(f"? Failed: {response.text}")
        return False

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
    if response1.status_code == 200:
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
    if response2.status_code == 200:
        data2 = response2.json()
        response_text = data2.get('response', '').lower()
        print(f"? Response: {data2.get('response')}")
        print(f"? Conversation Length: {data2.get('conversation_length')}")
        
        if 'python' in response_text:
            print("? Claude remembered the conversation!")
        else:
            print("? Memory check uncertain")
    
    # Third message - search with history
    if BRAVE_KEY:
        print("\n?? Message 3: Search query with context...")
        payload3 = {
            "prompt": "What are the latest updates for my favorite language?",
            "conversation_id": conversation_id,
            "max_tokens": 200,
            "enable_search": True
        }
        
        response3 = client.post("/ai/generate", json=payload3)
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"? Response Length: {len(data3.get('response', ''))}")
            print(f"? Conversation Length: {data3.get('conversation_length')}")
            print(f"? Search Enabled: {data3.get('search_enabled')}")
            print(f"\n?? Response Preview:")
            print(f"   {data3.get('response', '')[:200]}...")
    
    # Clean up
    print("\n?? Cleaning up conversation...")
    cleanup = client.post("/ai/conversation/clear", json={"conversation_id": conversation_id})
    if cleanup.status_code == 200:
        print("? Conversation cleared")
    
    return True

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
    
    if response.status_code == 200:
        data = response.json()
        print(f"? Is Safe: {data.get('is_safe')}")
        print(f"? Reason: {data.get('reason')}")
        print(f"? Confidence: {data.get('confidence')}")
        return True
    else:
        print(f"? Failed: {response.text}")
        return False

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
        client.post("/ai/generate", json=payload)
    
    # Get count
    print("\n?? Getting conversation count...")
    count_response = client.get(f"/ai/conversation/{conv_id}/count")
    if count_response.status_code == 200:
        data = count_response.json()
        print(f"? Message Count: {data.get('message_count')}")
    
    # Get history
    print("\n?? Getting conversation history...")
    history_response = client.get(f"/ai/conversation/{conv_id}/history")
    if history_response.status_code == 200:
        data = history_response.json()
        print(f"? Retrieved {data.get('message_count')} messages")
    
    # Clear
    print("\n?? Clearing conversation...")
    clear_response = client.post("/ai/conversation/clear", json={"conversation_id": conv_id})
    if clear_response.status_code == 200:
        print("? Conversation cleared successfully")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("\n?? Starting Comprehensive Test Suite...")
    
    results = []
    
    # Test 1: Health Check
    try:
        results.append(("Health Check", test_health_check()))
    except Exception as e:
        print(f"? Health Check Error: {e}")
        results.append(("Health Check", False))
    
    # Test 2: Generate without search
    try:
        results.append(("Generate (No Search)", test_generate_without_search()))
    except Exception as e:
        print(f"? Generate (No Search) Error: {e}")
        results.append(("Generate (No Search)", False))
    
    # Test 3: Generate with search
    try:
        results.append(("Generate (With Search)", test_generate_with_search()))
    except Exception as e:
        print(f"? Generate (With Search) Error: {e}")
        results.append(("Generate (With Search)", False))
    
    # Test 4: Conversation history
    try:
        results.append(("Conversation History", test_conversation_history()))
    except Exception as e:
        print(f"? Conversation History Error: {e}")
        results.append(("Conversation History", False))
    
    # Test 5: Content moderation
    try:
        results.append(("Content Moderation", test_content_moderation()))
    except Exception as e:
        print(f"? Content Moderation Error: {e}")
        results.append(("Content Moderation", False))
    
    # Test 6: Conversation endpoints
    try:
        results.append(("Conversation Management", test_conversation_endpoints()))
    except Exception as e:
        print(f"? Conversation Management Error: {e}")
        results.append(("Conversation Management", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("?? TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    for test_name, result in results:
        if result is True:
            print(f"? {test_name}: PASSED")
        elif result is False:
            print(f"? {test_name}: FAILED")
        else:
            print(f"? {test_name}: SKIPPED")
    
    print(f"\n?? Results: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0:
        print("\n?? All tests passed!")
    else:
        print(f"\n? {failed} test(s) failed")
    
    return failed == 0

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n? Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n? Fatal error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
