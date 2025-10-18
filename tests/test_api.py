import pytest
from fastapi.testclient import TestClient
import main_optimized

client = TestClient(main_optimized.app)

def test_health():
    r = client.get('/health')
    assert r.status_code == 200
    assert 'status' in r.json()

def test_create_user_and_room_and_join():
    # create user
    r = client.post('/users', json={'username': 'tester'})
    assert r.status_code == 200
    user = r.json()
    assert 'id' in user

    # create room
    r2 = client.post('/rooms', json={'name': 'room1'})
    assert r2.status_code == 200
    room = r2.json()
    assert 'id' in room

    # join room
    r3 = client.post(f"/rooms/{room['id']}/join", json={'user_id': user['id']})
    assert r3.status_code == 200
    assert 'message' in r3.json()

@pytest.mark.asyncio
async def test_websocket_smoke():
    # Create user
    r = client.post('/users', json={'username': 'ws_tester'})
    assert r.status_code == 200
    user = r.json()

    # Create room
    r2 = client.post('/rooms', json={'name': 'ws_room'})
    assert r2.status_code == 200
    room = r2.json()

    # Join
    r3 = client.post(f"/rooms/{room['id']}/join", json={'user_id': user['id']})
    assert r3.status_code == 200

    # Connect websocket properly
    with client.websocket_connect(f"/ws/{room['id']}/{user['id']}") as ws2:
        # send a chat message payload
        ws2.send_text('{"content": "hello"}')
        # read broadcast (join + message) - there may be more than one message; at least one should arrive
        data = ws2.receive_text()
        assert data
