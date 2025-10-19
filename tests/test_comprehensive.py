"""
Comprehensive test suite for FastAPI Video Chat Application
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock


# Fixtures
@pytest.fixture
def client():
    """Create test client"""
    from main import app
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample user data"""
    return {"username": "test_user"}


@pytest.fixture
def test_room_data():
    """Sample room data"""
    return {"name": "test_room"}


# Health and Info Tests
class TestHealthAndInfo:
    """Tests for health check and info endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "2.0.0"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data
        assert "stats" in data
    
    def test_debug_endpoint(self, client):
        """Test debug endpoint"""
        response = client.get("/_debug")
        assert response.status_code == 200
        data = response.json()
        assert "bunny_enabled" in data
        assert "environment" in data


# User Management Tests
class TestUserManagement:
    """Tests for user-related endpoints"""
    
    def test_create_user_success(self, client, test_user_data):
        """Test successful user creation"""
        response = client.post("/users", json=test_user_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["username"] == test_user_data["username"]
        assert "joined_at" in data
    
    def test_create_user_invalid_username(self, client):
        """Test user creation with invalid username"""
        response = client.post("/users", json={"username": "a"})
        assert response.status_code == 422  # Validation error
    
    def test_get_all_users(self, client, test_user_data):
        """Test getting all users"""
        # Create a user first
        client.post("/users", json=test_user_data)
        
        response = client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1


# Room Management Tests
class TestRoomManagement:
    """Tests for room-related endpoints"""
    
    def test_create_room_success(self, client, test_room_data):
        """Test successful room creation"""
        response = client.post("/rooms", json=test_room_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == test_room_data["name"]
        assert "created_at" in data
    
    def test_get_all_rooms(self, client, test_room_data):
        """Test getting all rooms"""
        # Create a room first
        client.post("/rooms", json=test_room_data)
        
        response = client.get("/rooms")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_room_by_id(self, client, test_room_data):
        """Test getting specific room"""
        # Create room
        create_response = client.post("/rooms", json=test_room_data)
        room_id = create_response.json()["id"]
        
        # Get room
        response = client.get(f"/rooms/{room_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == room_id
    
    def test_get_nonexistent_room(self, client):
        """Test getting room that doesn't exist"""
        response = client.get("/rooms/nonexistent-id")
        assert response.status_code == 404
    
    def test_join_room_success(self, client, test_user_data, test_room_data):
        """Test successful room joining"""
        # Create user and room
        user_response = client.post("/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        # Join room
        response = client.post(
            f"/rooms/{room_id}/join",
            json={"user_id": user_id}
        )
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_join_nonexistent_room(self, client, test_user_data):
        """Test joining room that doesn't exist"""
        user_response = client.post("/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        response = client.post(
            "/rooms/nonexistent-id/join",
            json={"user_id": user_id}
        )
        assert response.status_code == 404


# Message Tests
class TestMessages:
    """Tests for message-related endpoints"""
    
    def test_get_room_messages_empty(self, client, test_room_data):
        """Test getting messages from empty room"""
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        response = client.get(f"/rooms/{room_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_messages_from_nonexistent_room(self, client):
        """Test getting messages from room that doesn't exist"""
        response = client.get("/rooms/nonexistent-id/messages")
        assert response.status_code == 404


# WebSocket Tests
class TestWebSocket:
    """Tests for WebSocket functionality"""
    
    def test_websocket_connection_success(self, client, test_user_data, test_room_data):
        """Test successful WebSocket connection"""
        # Create user and room
        user_response = client.post("/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        # Connect via WebSocket
        with client.websocket_connect(f"/ws/{room_id}/{user_id}") as websocket:
            # Should receive join message
            data = websocket.receive_text()
            assert data is not None
    
    def test_websocket_send_message(self, client, test_user_data, test_room_data):
        """Test sending message via WebSocket"""
        # Create user and room
        user_response = client.post("/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        # Connect and send message
        with client.websocket_connect(f"/ws/{room_id}/{user_id}") as websocket:
            # Skip join message
            websocket.receive_text()
            
            # Send chat message
            websocket.send_text('{"content": "Hello, World!"}')
            
            # Should receive the message back
            response = websocket.receive_text()
            assert "Hello, World!" in response
    
    def test_websocket_invalid_room(self, client, test_user_data):
        """Test WebSocket connection with invalid room"""
        user_response = client.post("/users", json=test_user_data)
        user_id = user_response.json()["id"]
        
        with pytest.raises(Exception):
            with client.websocket_connect(f"/ws/invalid-room/{user_id}"):
                pass


# Video Integration Tests
class TestVideoIntegration:
    """Tests for video-related endpoints"""
    
    @patch('requests.post')
    def test_create_live_stream_mock(self, mock_post, client, test_room_data):
        """Test live stream creation with mocked Bunny API"""
        # Create room
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        # Mock Bunny API response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "id": "stream-123",
            "streamKey": "test-stream-key"
        }
        
        # Create live stream
        response = client.post(
            f"/rooms/{room_id}/live-stream",
            json={"title": "Test Stream"}
        )
        
        # Note: Will fall back to mock if Bunny not configured
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "stream_key" in data
    
    def test_get_room_live_streams(self, client, test_room_data):
        """Test getting live streams for a room"""
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        response = client.get(f"/rooms/{room_id}/live-streams")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_room_videos(self, client, test_room_data):
        """Test getting videos for a room"""
        room_response = client.post("/rooms", json=test_room_data)
        room_id = room_response.json()["id"]
        
        response = client.get(f"/rooms/{room_id}/videos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# Performance Tests
class TestPerformance:
    """Performance and load tests"""
    
    def test_concurrent_user_creation(self, client):
        """Test creating multiple users concurrently"""
        import concurrent.futures
        
        def create_user(index):
            return client.post("/users", json={"username": f"user_{index}"})
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_user, i) for i in range(50)]
            results = [f.result() for f in futures]
        
        # All should succeed
        assert all(r.status_code == 200 for r in results)
    
    def test_rapid_room_creation(self, client):
        """Test creating rooms rapidly"""
        responses = []
        for i in range(20):
            response = client.post("/rooms", json={"name": f"room_{i}"})
            responses.append(response)
        
        assert all(r.status_code == 200 for r in responses)


# Integration Tests
class TestIntegration:
    """Full workflow integration tests"""
    
    def test_full_chat_workflow(self, client):
        """Test complete chat workflow"""
        # 1. Create users
        user1 = client.post("/users", json={"username": "alice"}).json()
        user2 = client.post("/users", json={"username": "bob"}).json()
        
        # 2. Create room
        room = client.post("/rooms", json={"name": "general"}).json()
        
        # 3. Users join room
        client.post(f"/rooms/{room['id']}/join", json={"user_id": user1['id']})
        client.post(f"/rooms/{room['id']}/join", json={"user_id": user2['id']})
        
        # 4. Connect via WebSocket and send messages
        with client.websocket_connect(f"/ws/{room['id']}/{user1['id']}") as ws1:
            # Skip join message
            ws1.receive_text()
            
            # Send message
            ws1.send_text('{"content": "Hello from Alice!"}')
            message = ws1.receive_text()
            assert "Alice" in message
        
        # 5. Check message history
        messages = client.get(f"/rooms/{room['id']}/messages").json()
        assert len(messages) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
