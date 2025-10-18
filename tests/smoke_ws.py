import json
import sys
import os
from fastapi.testclient import TestClient

# Ensure repo root is on sys.path so we can import the app module when running from tests/
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

import main_optimized as m

client = TestClient(m.app)

print('Creating user...')
r = client.post('/users', json={'username': 'tester'})
print('POST /users', r.status_code, r.text)
user = r.json()

print('Creating room...')
r2 = client.post('/rooms', json={'name': 'room1'})
print('POST /rooms', r2.status_code, r2.text)
room = r2.json()

print('Joining room...')
r3 = client.post(f"/rooms/{room['id']}/join", json={'user_id': user['id']})
print('POST /rooms/{id}/join', r3.status_code, r3.text)

print('Opening websocket...')
with client.websocket_connect(f"/ws/{room['id']}/{user['id']}") as ws:
    print('WebSocket connected')
    # receive the join notification broadcast
    join_msg = ws.receive_text()
    print('Received (join):', join_msg)
    # send a message
    ws.send_text(json.dumps({'content': 'hello from tester'}))
    # receive the broadcasted message
    msg = ws.receive_text()
    print('Received (message):', msg)

print('Check messages endpoint...')
msgs = client.get(f"/rooms/{room['id']}/messages")
print('GET /rooms/{id}/messages', msgs.status_code, msgs.text)

print('Smoke test complete')
