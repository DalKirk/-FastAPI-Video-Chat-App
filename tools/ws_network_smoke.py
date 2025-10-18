"""Network-level WebSocket smoke test.

Usage: run this while Uvicorn is running (python tools/ws_network_smoke.py).
It will:
 - create a user
 - create a room
 - join the room
 - open a real websocket to ws://127.0.0.1:8000/ws/{room_id}/{user_id}
 - receive the join broadcast then send a message and receive the broadcast

Requires: httpx and websockets (installed in the project's venv).
"""
import asyncio
import json
import os
import sys

import httpx
import websockets


API_BASE = os.getenv('API_BASE', 'http://127.0.0.1:8000')
WS_BASE = os.getenv('WS_BASE', 'ws://127.0.0.1:8000')


async def main():
    print('Using API base:', API_BASE)
    async with httpx.AsyncClient(base_url=API_BASE, timeout=10) as client:
        # Create user
        print('Creating user...')
        r = await client.post('/users', json={'username': 'nettester'})
        r.raise_for_status()
        user = r.json()
        print('User:', user)

        # Create room
        print('Creating room...')
        r2 = await client.post('/rooms', json={'name': 'netroom'})
        r2.raise_for_status()
        room = r2.json()
        print('Room:', room)

        # Join room
        print('Joining room...')
        r3 = await client.post(f"/rooms/{room['id']}/join", json={'user_id': user['id']})
        r3.raise_for_status()
        print('Joined room')

    ws_url = f"{WS_BASE}/ws/{room['id']}/{user['id']}"
    print('Connecting to WebSocket at', ws_url)

    try:
        async with websockets.connect(ws_url, max_size=2**20) as ws:
            print('WebSocket connected')
            # receive join broadcast
            join_msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print('Received (join):', join_msg)

            # send a message
            payload = json.dumps({'content': 'hello from nettester'})
            print('Sending message:', payload)
            await ws.send(payload)

            # receive broadcasted message
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            print('Received (message):', msg)

    except Exception as e:
        print('WebSocket error:', repr(e))
        sys.exit(2)

    print('Network WebSocket smoke test complete')


if __name__ == '__main__':
    asyncio.run(main())
