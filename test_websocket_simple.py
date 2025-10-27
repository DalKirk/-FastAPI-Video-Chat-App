#!/usr/bin/env python3
"""
Simple WebSocket test using FastAPI's TestClient
"""
import json
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from fastapi.testclient import TestClient
    import main
    print("? Successfully imported main module")
except ImportError as e:
    print(f"? Import error: {e}")
    sys.exit(1)

def test_websocket_basic():
    """Test basic WebSocket functionality"""
    print("?? Testing WebSocket with TestClient...")
    
    try:
        client = TestClient(main.app)
        
        # 1. Create user
        print("1. Creating user...")
        user_response = client.post('/users', json={'username': 'test_user'})
        if user_response.status_code != 200:
            print(f"? User creation failed: {user_response.status_code} - {user_response.text}")
            return False
        user = user_response.json()
        print(f"? User created: {user['username']}")
        
        # 2. Create room
        print("2. Creating room...")
        room_response = client.post('/rooms', json={'name': 'test_room'})
        if room_response.status_code != 200:
            print(f"? Room creation failed: {room_response.status_code} - {room_response.text}")
            return False
        room = room_response.json()
        print(f"? Room created: {room['name']}")
        
        # 3. Test WebSocket
        print("3. Testing WebSocket connection...")
        with client.websocket_connect(f"/ws/{room['id']}/{user['id']}") as websocket:
            print("? WebSocket connected successfully")
            
            # Receive join message
            join_data = websocket.receive_text()
            join_msg = json.loads(join_data)
            print(f"? Join message: {join_msg.get('message', join_msg)}")
            
            # Send a test message
            test_message = {'content': 'Hello WebSocket!'}
            websocket.send_text(json.dumps(test_message))
            print("? Test message sent")
            
            # Receive the broadcast
            response_data = websocket.receive_text()
            response_msg = json.loads(response_data)
            print(f"? Message broadcast: {response_msg.get('content', response_msg)}")
            
            return True
            
    except Exception as e:
        print(f"? WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test basic API endpoints"""
    print("?? Testing API endpoints...")
    
    try:
        client = TestClient(main.app)
        
        # Health check
        health = client.get('/health')
        if health.status_code == 200:
            print("? Health endpoint works")
        else:
            print(f"? Health endpoint failed: {health.status_code}")
            return False
        
        # Root endpoint
        root = client.get('/')
        if root.status_code == 200:
            print("? Root endpoint works")
        else:
            print(f"? Root endpoint failed: {root.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"? API test failed: {e}")
        return False

def main_test():
    """Main test function"""
    print("?? FastAPI WebSocket Test")
    print("=" * 50)
    
    # Test API endpoints first
    api_ok = test_api_endpoints()
    if not api_ok:
        print("? API tests failed - stopping")
        return 1
    
    # Test WebSocket
    ws_ok = test_websocket_basic()
    
    print("\n" + "=" * 50)
    if api_ok and ws_ok:
        print("?? ALL TESTS PASSED!")
        print("? WebSocket implementation is working correctly")
        print("\n?? To run the server:")
        print("python -m uvicorn main:app --reload")
        print("Then visit: http://localhost:8000/chat")
        return 0
    else:
        print("? SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main_test())