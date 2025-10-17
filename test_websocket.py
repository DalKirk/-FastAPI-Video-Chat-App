import asyncio
import websockets
import json
import requests

async def test_deployed_backend():
    print("🧪 Testing deployed backend full flow...")

    BASE_URL = "https://natural-presence-production.up.railway.app"

    # Step 1: Create user
    print("\n1. Creating user...")
    user_response = requests.post(f'{BASE_URL}/users', json={'username': 'testuser_deployed'})
    if not user_response.ok:
        print(f"❌ Failed to create user: {user_response.text}")
        return

    user = user_response.json()
    print(f"✅ Created user: {user}")

    # Step 2: Create room
    print("\n2. Creating room...")
    room_response = requests.post(f'{BASE_URL}/rooms', json={'name': 'testroom_deployed'})
    if not room_response.ok:
        print(f"❌ Failed to create room: {room_response.text}")
        return

    room = room_response.json()
    print(f"✅ Created room: {room}")

    # Step 3: Join room
    print("\n3. Joining room...")
    join_response = requests.post(f'{BASE_URL}/rooms/{room["id"]}/join', json={'user_id': user['id']})
    if not join_response.ok:
        print(f"❌ Failed to join room: {join_response.text}")
        return

    print("✅ Joined room successfully")

    # Step 4: Test WebSocket connection and messaging
    print("\n4. Testing WebSocket messaging...")
    uri = f"wss://natural-presence-production.up.railway.app/ws/{room['id']}/{user['id']}"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")

            # Wait for join message
            try:
                join_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Join message: {join_msg}")
            except asyncio.TimeoutError:
                print("⏰ No join message received (this is OK)")

            # Send a test message
            test_message = {"content": "Hello from deployed backend test!"}
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent message: {test_message}")

            # Wait for broadcast
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received broadcast: {response}")
                print("✅ Message sending works!")
            except asyncio.TimeoutError:
                print("⏰ No broadcast received - message sending may not work")

            print("✅ WebSocket test completed!")

    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_deployed_backend())