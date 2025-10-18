import asyncio
import websockets
import json
import requests
import time
import pytest

@pytest.mark.asyncio
async def test_timestamps():
    print('🧪 Testing timestamp storage and retrieval...')

    BASE_URL = 'https://natural-presence-production.up.railway.app'

    # Create user and room
    user_response = requests.post(f'{BASE_URL}/users', json={'username': 'timestamp_test'})
    user = user_response.json()
    print(f'Created user: {user["username"]}')

    room_response = requests.post(f'{BASE_URL}/rooms', json={'name': 'timestamp_room'})
    room = room_response.json()
    print(f'Created room: {room["name"]}')

    # Join room
    requests.post(f'{BASE_URL}/rooms/{room["id"]}/join', json={'user_id': user["id"]})

    uri = f'wss://natural-presence-production.up.railway.app/ws/{room["id"]}/{user["id"]}'

    try:
        async with websockets.connect(uri) as websocket:
            print('✅ WebSocket connected')

            # Wait for join message
            join_msg = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            join_data = json.loads(join_msg)
            print(f'📥 Join message timestamp: {join_data["timestamp"]}')

            # Send a message
            test_message = {'content': 'Test message for timestamp'}
            await websocket.send(json.dumps(test_message))

            # Receive the message back
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            response_data = json.loads(response)
            print(f'📤 Sent message timestamp: {response_data["timestamp"]}')

            # Wait a moment for processing
            await asyncio.sleep(2)

            # Now check what the API returns
            messages_response = requests.get(f'{BASE_URL}/rooms/{room["id"]}/messages')
            messages = messages_response.json()

            print(f'📚 API returned {len(messages)} messages')
            for i, msg in enumerate(messages):
                print(f'  Message {i+1}: {msg["content"]} - timestamp: {msg["timestamp"]}')

    except Exception as e:
        print(f'❌ Error: {e}')