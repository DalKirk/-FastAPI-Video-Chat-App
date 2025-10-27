#!/usr/bin/env python3
"""
Test WebSocket connectivity and functionality
"""
import asyncio
import json
import sys
import os
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    import httpx
    import websockets
    print("? Required packages (httpx, websockets) are available")
except ImportError as e:
    print(f"? Missing required packages: {e}")
    print("Install with: pip install httpx websockets")
    sys.exit(1)

# Configuration
API_BASE = os.getenv('API_BASE', 'http://127.0.0.1:8000')
WS_BASE = os.getenv('WS_BASE', 'ws://127.0.0.1:8000')

async def test_websocket_connection():
    """Test complete WebSocket flow"""
    print(f"?? Testing WebSocket connection to {API_BASE}")
    
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
            # 1. Health check
            print("1. Health check...")
            health_response = await client.get('/health')
            if health_response.status_code != 200:
                print(f"? Health check failed: {health_response.status_code}")
                return False
            print("? Health check passed")
            
            # 2. Create user
            print("2. Creating user...")
            user_response = await client.post('/users', json={'username': 'test_user'})
            if user_response.status_code != 200:
                print(f"? User creation failed: {user_response.status_code} - {user_response.text}")
                return False
            user = user_response.json()
            print(f"? User created: {user['username']} ({user['id']})")
            
            # 3. Create room
            print("3. Creating room...")
            room_response = await client.post('/rooms', json={'name': 'test_room'})
            if room_response.status_code != 200:
                print(f"? Room creation failed: {room_response.status_code} - {room_response.text}")
                return False
            room = room_response.json()
            print(f"? Room created: {room['name']} ({room['id']})")
            
            # 4. Test WebSocket connection
            print("4. Testing WebSocket connection...")
            ws_url = f"{WS_BASE}/ws/{room['id']}/{user['id']}"
            print(f"Connecting to: {ws_url}")
            
            try:
                async with websockets.connect(ws_url, max_size=2**20) as websocket:
                    print("? WebSocket connected successfully")
                    
                    # 5. Wait for join message
                    print("5. Waiting for join message...")
                    join_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    join_data = json.loads(join_msg)
                    print(f"? Join message received: {join_data.get('message', join_data)}")
                    
                    # 6. Send test message
                    print("6. Sending test message...")
                    test_message = {'content': 'Hello from WebSocket test!'}
                    await websocket.send(json.dumps(test_message))
                    print("? Message sent")
                    
                    # 7. Receive broadcast message
                    print("7. Waiting for message broadcast...")
                    msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    msg_data = json.loads(msg)
                    print(f"? Message broadcast received: {msg_data.get('content', msg_data)}")
                    
                    # 8. Test message history
                    print("8. Testing message history...")
                    history_response = await client.get(f"/rooms/{room['id']}/messages")
                    if history_response.status_code == 200:
                        messages = history_response.json()
                        print(f"? Message history retrieved: {len(messages)} messages")
                    else:
                        print(f"??  Message history failed: {history_response.status_code}")
                    
                    print("?? All WebSocket tests passed!")
                    return True
                    
            except websockets.exceptions.ConnectionClosed as e:
                print(f"? WebSocket connection closed unexpectedly: {e}")
                return False
            except asyncio.TimeoutError:
                print("? WebSocket timeout - no response received")
                return False
            except Exception as e:
                print(f"? WebSocket error: {e}")
                return False
                
    except httpx.ConnectError:
        print(f"? Cannot connect to API at {API_BASE}")
        print("Make sure the server is running with: python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"? Unexpected error: {e}")
        return False

async def test_websocket_error_handling():
    """Test WebSocket error scenarios"""
    print("\n?? Testing WebSocket error handling...")
    
    try:
        # Test invalid room
        invalid_ws_url = f"{WS_BASE}/ws/invalid-room-id/invalid-user-id"
        print(f"Testing invalid room/user: {invalid_ws_url}")
        
        try:
            async with websockets.connect(invalid_ws_url, max_size=2**20) as websocket:
                print("? Connection should have failed for invalid room/user")
                return False
        except websockets.exceptions.ConnectionClosedError as e:
            if e.code == 4004:
                print("? Correctly rejected invalid room/user")
            else:
                print(f"??  Unexpected close code: {e.code}")
        except Exception as e:
            print(f"? Connection properly rejected: {e}")
            
        return True
        
    except Exception as e:
        print(f"? Error handling test failed: {e}")
        return False

def print_diagnostics():
    """Print diagnostic information"""
    print("\n?? WebSocket Diagnostics:")
    print(f"API Base URL: {API_BASE}")
    print(f"WebSocket Base URL: {WS_BASE}")
    print(f"Python version: {sys.version}")
    
    # Check if server is running
    try:
        import requests
        response = requests.get(f"{API_BASE}/health", timeout=5)
        print(f"Server status: {'? Running' if response.status_code == 200 else '? Error'}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"Server version: {health_data.get('version', 'unknown')}")
            print(f"WebSocket service: {health_data.get('services', {}).get('websocket', 'unknown')}")
    except Exception as e:
        print(f"Server status: ? Not reachable ({e})")

async def main():
    """Main test function"""
    print("?? WebSocket Connection Test")
    print("=" * 50)
    
    print_diagnostics()
    
    # Test basic WebSocket functionality
    basic_test_passed = await test_websocket_connection()
    
    # Test error handling
    error_test_passed = await test_websocket_error_handling()
    
    print("\n" + "=" * 50)
    if basic_test_passed and error_test_passed:
        print("?? ALL TESTS PASSED - WebSocket is working correctly!")
        return 0
    else:
        print("? SOME TESTS FAILED - Check the output above")
        return 1

if __name__ == '__main__':
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n??  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n?? Test crashed: {e}")
        sys.exit(2)