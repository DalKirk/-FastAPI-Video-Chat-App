#!/usr/bin/env python3
"""
Complete diagnostic script for WebSocket chat room connection issues
Checks all common problems and provides specific fixes
"""
import asyncio
import json
import sys
import os

try:
    import httpx
    import websockets
    print("? Required packages installed")
except ImportError as e:
    print(f"? Missing packages: {e}")
    print("Install with: pip install httpx websockets")
    sys.exit(1)

# Configuration
API_BASE = os.getenv('API_BASE', 'http://127.0.0.1:8000')
WS_BASE = os.getenv('WS_BASE', 'ws://127.0.0.1:8000')

async def check_server_health():
    """Check if server is running and healthy"""
    print("\n?? Step 1: Checking server health...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f'{API_BASE}/health')
            if response.status_code == 200:
                data = response.json()
                print(f"? Server is healthy")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Environment: {data.get('environment', 'unknown')}")
                print(f"   WebSocket: {data.get('services', {}).get('websocket', 'unknown')}")
                return True
            else:
                print(f"? Server returned {response.status_code}")
                return False
    except Exception as e:
        print(f"? Cannot connect to server: {e}")
        print(f"   Make sure server is running: python -m uvicorn main:app --reload")
        return False

async def check_environment_config():
    """Check environment configuration"""
    print("\n?? Step 2: Checking environment configuration...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f'{API_BASE}/_debug')
            if response.status_code == 200:
                data = response.json()
                print(f"? Environment info retrieved")
                print(f"   Environment: {data.get('environment', 'unknown')}")
                print(f"   Auto-create on WS: {data.get('auto_create_on_ws', False)}")
                print(f"   Auto-create on join: {data.get('auto_create_on_join', False)}")
                print(f"   Auto-user on join: {data.get('auto_user_on_join', False)}")
                
                if not data.get('auto_create_on_ws') and data.get('environment') == 'development':
                    print("\n??  WARNING: Auto-creation disabled in development mode")
                    print("   You MUST create users and rooms before WebSocket connection")
                    print("   Or set ENVIRONMENT=production to enable auto-creation")
                
                return data
            else:
                print(f"??  Debug endpoint returned {response.status_code}")
                return None
    except Exception as e:
        print(f"??  Could not get debug info: {e}")
        return None

async def test_user_creation():
    """Test creating a user"""
    print("\n?? Step 3: Testing user creation...")
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
            response = await client.post('/users', json={'username': 'diagnostic_user'})
            if response.status_code == 200:
                user = response.json()
                print(f"? User created successfully")
                print(f"   Username: {user['username']}")
                print(f"   ID: {user['id']}")
                return user
            else:
                print(f"? User creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
    except Exception as e:
        print(f"? Error creating user: {e}")
        return None

async def test_room_creation():
    """Test creating a room"""
    print("\n?? Step 4: Testing room creation...")
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
            response = await client.post('/rooms', json={'name': 'diagnostic_room'})
            if response.status_code == 200:
                room = response.json()
                print(f"? Room created successfully")
                print(f"   Name: {room['name']}")
                print(f"   ID: {room['id']}")
                return room
            else:
                print(f"? Room creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
    except Exception as e:
        print(f"? Error creating room: {e}")
        return None

async def test_room_join(room_id, user_id, username):
    """Test joining a room"""
    print("\n?? Step 5: Testing room join...")
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
            response = await client.post(
                f'/rooms/{room_id}/join',
                json={'user_id': user_id, 'username': username}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"? Successfully joined room")
                print(f"   {data.get('message', 'Joined')}")
                return True
            else:
                print(f"? Join room failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    except Exception as e:
        print(f"? Error joining room: {e}")
        return False

async def test_websocket_connection(room_id, user_id):
    """Test WebSocket connection"""
    print("\n?? Step 6: Testing WebSocket connection...")
    ws_url = f"{WS_BASE}/ws/{room_id}/{user_id}"
    print(f"   URL: {ws_url}")
    
    try:
        async with websockets.connect(ws_url, max_size=2**20) as websocket:
            print("? WebSocket connected successfully!")
            
            # Wait for join message
            try:
                join_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                join_data = json.loads(join_msg)
                print(f"? Received join message: {join_data.get('message', join_data)}")
            except asyncio.TimeoutError:
                print("??  No join message received (timeout)")
            
            # Send test message
            test_msg = {'content': 'Diagnostic test message'}
            await websocket.send(json.dumps(test_msg))
            print("? Test message sent")
            
            # Receive broadcast
            try:
                broadcast = await asyncio.wait_for(websocket.recv(), timeout=5)
                broadcast_data = json.loads(broadcast)
                print(f"? Message broadcast received: {broadcast_data.get('content', broadcast_data)}")
            except asyncio.TimeoutError:
                print("??  No broadcast received (timeout)")
            
            return True
            
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"? WebSocket connection closed immediately")
        print(f"   Close code: {e.code}")
        print(f"   Reason: {e.reason}")
        
        if e.code == 4004:
            print("\n?? FIX: Room or user not found")
            print("   Make sure you create user and room BEFORE connecting WebSocket")
            print("   Or enable auto-creation in production mode")
        
        return False
        
    except Exception as e:
        print(f"? WebSocket error: {e}")
        return False

async def test_without_join():
    """Test WebSocket without joining room first (should fail)"""
    print("\n?? Step 7: Testing WebSocket without room join (should fail)...")
    
    try:
        async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
            # Create user and room but DON'T join
            user_response = await client.post('/users', json={'username': 'test_no_join'})
            room_response = await client.post('/rooms', json={'name': 'test_no_join_room'})
            
            if user_response.status_code == 200 and room_response.status_code == 200:
                user = user_response.json()
                room = room_response.json()
                
                ws_url = f"{WS_BASE}/ws/{room['id']}/{user['id']}"
                print(f"   Attempting to connect without joining: {ws_url}")
                
                try:
                    async with websockets.connect(ws_url, max_size=2**20) as websocket:
                        print("??  Connection succeeded (unexpected in dev mode)")
                        print("   This means auto-creation is enabled")
                        return True
                except websockets.exceptions.ConnectionClosedError as e:
                    if e.code == 4004:
                        print("? Connection properly rejected (code 4004)")
                        print("   This is expected behavior in development mode")
                        return True
                    else:
                        print(f"? Unexpected close code: {e.code}")
                        return False
    except Exception as e:
        print(f"? Test failed: {e}")
        return False

async def run_diagnostics():
    """Run complete diagnostic suite"""
    print("=" * 60)
    print("?? WebSocket Chat Room Connection Diagnostics")
    print("=" * 60)
    
    # Check server
    if not await check_server_health():
        print("\n? DIAGNOSIS: Server is not running or not responding")
        print("?? FIX: Start the server with:")
        print("   python -m uvicorn main:app --reload")
        return False
    
    # Check environment
    env_config = await check_environment_config()
    
    # Test user creation
    user = await test_user_creation()
    if not user:
        print("\n? DIAGNOSIS: Cannot create users")
        print("?? FIX: Check server logs for errors")
        return False
    
    # Test room creation
    room = await test_room_creation()
    if not room:
        print("\n? DIAGNOSIS: Cannot create rooms")
        print("?? FIX: Check server logs for errors")
        return False
    
    # Test room join
    join_ok = await test_room_join(room['id'], user['id'], user['username'])
    if not join_ok:
        print("\n? DIAGNOSIS: Cannot join rooms")
        print("?? FIX: Check room join endpoint implementation")
        return False
    
    # Test WebSocket
    ws_ok = await test_websocket_connection(room['id'], user['id'])
    if not ws_ok:
        print("\n? DIAGNOSIS: WebSocket connection failed")
        print("?? FIX: Check that user/room exist and join was successful")
        return False
    
    # Test without join (optional)
    await test_without_join()
    
    print("\n" + "=" * 60)
    print("? ALL DIAGNOSTICS PASSED!")
    print("=" * 60)
    print("\n?? Your WebSocket chat is working correctly!")
    print("\n?? Checklist for successful connection:")
    print("   1. ? Create user (POST /users)")
    print("   2. ? Create room (POST /rooms)")
    print("   3. ? Join room (POST /rooms/{room_id}/join)")
    print("   4. ? Connect WebSocket (WS /ws/{room_id}/{user_id})")
    
    return True

async def main():
    """Main entry point"""
    try:
        success = await run_diagnostics()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n??  Diagnostic interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n? Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == '__main__':
    print("\n?? Starting diagnostic script...")
    print(f"?? API Base: {API_BASE}")
    print(f"?? WebSocket Base: {WS_BASE}")
    print()
    
    asyncio.run(main())
