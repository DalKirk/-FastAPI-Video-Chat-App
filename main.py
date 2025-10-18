from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid
import os
import base64
import requests

# Optional Mux imports - CORRECTED for mux-python 3.x
try:
    from mux_python import ApiClient as MuxApiClient, Configuration as MuxConfiguration
    from mux_python.api import direct_uploads_api, live_streams_api, assets_api
    from mux_python.model import CreateDirectUploadRequest, CreateLiveStreamRequest
    MUX_AVAILABLE = True
except ImportError:
    MUX_AVAILABLE = False
    print("⚠️ Mux-python not available - video features disabled")

app = FastAPI(title="Chat API with Video", description="Real-time messaging API with WebSocket support and video streaming")

# Mux Configuration - Environment Variables
MUX_TOKEN_ID = os.getenv("MUX_TOKEN_ID", "9750d6c6-011b-44cd-94df-23da0aaafd51")
MUX_TOKEN_SECRET = os.getenv("MUX_TOKEN_SECRET", "BEWYJ8Vsbdt6bB3v0CN/OhqCEWJVImhp5M7sSdaASL1cS1xmdmxLpCKzAY5KRN0qNcmmhmHroch")
MUX_ENVIRONMENT_ID = os.getenv("MUX_ENVIRONMENT_ID", "6i6puunpacqp84md0rm11dmd0")

# Initialize Mux (Optional - graceful degradation if not available)
mux_enabled = False
assets_api = live_streams_api = direct_uploads_api = None

if MUX_AVAILABLE and MUX_TOKEN_ID and MUX_TOKEN_SECRET:
    try:
        # CORRECTED: Use proper mux-python 3.x configuration
        configuration = MuxConfiguration()
        configuration.username = MUX_TOKEN_ID
        configuration.password = MUX_TOKEN_SECRET
        
        # CORRECTED: Use proper API classes
        assets_api = assets_api.AssetsApi(MuxApiClient(configuration))
        live_streams_api = live_streams_api.LiveStreamsApi(MuxApiClient(configuration))
        direct_uploads_api = direct_uploads_api.DirectUploadsApi(MuxApiClient(configuration))
        
        mux_enabled = True
        print("✅ Mux API configured successfully")
    except Exception as e:
        mux_enabled = False
        print(f"⚠️ Mux configuration failed: {e}")
else:
    print("⚠️ Mux not available - video features disabled")

# Add CORS middleware for mobile browser compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://localhost:3000",
        "https://next-js-14-front-end-for-chat-plast.vercel.app",  # Primary Vercel frontend
        "https://video-chat-frontend-ruby.vercel.app",  # Alternative Vercel frontend
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Data Models
class User(BaseModel):
    id: str
    username: str
    joined_at: datetime

class Message(BaseModel):
    id: str
    user_id: str
    username: str
    room_id: str
    content: str
    timestamp: str

class Room(BaseModel):
    id: str
    name: str
    created_at: datetime
    users: List[str] = []

class MessageCreate(BaseModel):
    content: str

class RoomCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str

class JoinRoomRequest(BaseModel):
    user_id: str

# Mux Video Models
class LiveStreamCreate(BaseModel):
    title: str

class VideoUploadCreate(BaseModel):
    title: str
    description: Optional[str] = None

class VideoUpload(BaseModel):
    id: str
    upload_url: str
    status: str
    room_id: str
    title: str
    created_at: datetime

class LiveStream(BaseModel):
    id: str
    stream_key: str
    playback_id: str
    status: str
    room_id: str
    title: str
    created_at: datetime

# In-memory storage (in production, use a database)
rooms: Dict[str, Room] = {}
messages: Dict[str, List[Message]] = {}
users: Dict[str, User] = {}
live_streams: Dict[str, LiveStream] = {}
video_assets: Dict[str, dict] = {}
video_uploads: Dict[str, VideoUpload] = {}

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)
        self.user_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id in self.active_connections:
            # Create a copy of the connections list to avoid modification during iteration
            connections = self.active_connections[room_id].copy()
            dead_connections = []
            
            for connection in connections:
                try:
                    await connection.send_text(message)
                except:
                    # Mark dead connections for removal
                    dead_connections.append(connection)
            
            # Remove dead connections after iteration
            for dead_connection in dead_connections:
                if dead_connection in self.active_connections[room_id]:
                    self.active_connections[room_id].remove(dead_connection)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    mux_status = "enabled" if mux_enabled else "disabled"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "mux-integration-fixed",
        "services": {
            "api": "running",
            "websocket": "running",
            "mux": mux_status
        },
        "note": "Mux integration updated to use correct SDK v3.x API"
    }

# Test Mux endpoint
@app.get("/test-mux")
async def test_mux():
    """Test Mux API connectivity"""
    if not mux_enabled:
        return {"status": "Mux not enabled"}
    
    try:
        # Test basic authentication with Mux
        import base64
        
        auth_string = f"{MUX_TOKEN_ID}:{MUX_TOKEN_SECRET}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple GET request to list uploads
        response = requests.get(
            'https://api.mux.com/video/v1/uploads',
            headers=headers
        )
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "response_code": response.status_code,
            "response_text": response.text[:500]  # Limit response size
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

manager = ConnectionManager()

# API Endpoints
@app.get("/")
def root():
    return {"message": "FastAPI Chat API is running! Visit /chat for the chat interface or /docs for API documentation."}

@app.post("/users", response_model=User)
def create_user(user_data: UserCreate):
    """Create a new user"""
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        username=user_data.username,
        joined_at=datetime.utcnow()  # Use UTC for consistency
    )
    users[user_id] = user
    return user

@app.get("/users", response_model=List[User])
def get_users():
    """Get all users"""
    return list(users.values())

@app.post("/rooms", response_model=Room)
def create_room(room_data: RoomCreate):
    """Create a new chat room"""
    room_id = str(uuid.uuid4())
    room = Room(
        id=room_id,
        name=room_data.name,
        created_at=datetime.utcnow()  # Use UTC for consistency
    )
    rooms[room_id] = room
    messages[room_id] = []
    return room

@app.get("/rooms", response_model=List[Room])
def get_rooms():
    """Get all chat rooms"""
    return list(rooms.values())

@app.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: str):
    """Get a specific room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_id]

@app.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50):
    """Get messages from a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    room_messages = messages.get(room_id, [])
    
    # Return messages with properly formatted UTC timestamps
    formatted_messages = []
    for msg in room_messages[-limit:]:
        formatted_messages.append({
            "id": msg.id,
            "user_id": msg.user_id,
            "username": msg.username,
            "room_id": msg.room_id,
            "content": msg.content,
            "timestamp": msg.timestamp
        })
    
    return formatted_messages

@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, join_data: JoinRoomRequest):
    """Join a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if join_data.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    if join_data.user_id not in rooms[room_id].users:
        rooms[room_id].users.append(join_data.user_id)
    
    return {"message": f"User {users[join_data.user_id].username} joined room {rooms[room_id].name}"}

# Mux Video Endpoints
@app.post("/rooms/{room_id}/live-stream")
async def create_live_stream(room_id: str, stream_data: LiveStreamCreate):
    """Create a live stream for a room using Mux API"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not mux_enabled:
        # Fallback to mock if Mux not available
        mock_stream_id = str(uuid.uuid4())
        mock_stream_key = f"mock_stream_key_{mock_stream_id[:8]}"
        mock_playback_id = f"mock_playback_{mock_stream_id[:8]}"
        
        live_stream = LiveStream(
            id=mock_stream_id,
            stream_key=mock_stream_key,
            playback_id=mock_playback_id,
            status="mock_ready",
            room_id=room_id,
            title=stream_data.title,
            created_at=datetime.utcnow()
        )
        live_streams[mock_stream_id] = live_stream
        
        return {
            "id": live_stream.id,
            "stream_key": live_stream.stream_key,
            "playback_id": live_stream.playback_id,
            "status": live_stream.status,
            "title": live_stream.title,
            "rtmp_url": "rtmp://mock-stream.example.com/live/",
            "note": "Mock implementation - Mux not configured"
        }
    
    try:
        # CORRECTED: Use proper mux-python 3.x API
        create_request = CreateLiveStreamRequest(
            playback_policy=["public"],
            new_asset_settings={
                "playback_policies": ["public"]
            },
            test=False  # Set to False for production
        )
        
        # CORRECTED: Use correct API method
        stream_response = live_streams_api.create_live_stream(create_request)
        
        # Store live stream info
        live_stream = LiveStream(
            id=stream_response.data.id,
            stream_key=stream_response.data.stream_key,
            playback_id=stream_response.data.playback_id,
            status="ready",
            room_id=room_id,
            title=stream_data.title,
            created_at=datetime.utcnow()
        )
        
        live_streams[stream_response.data.id] = live_stream
        
        # Notify room about new live stream
        stream_message = {
            "type": "live_stream_created",
            "stream_id": live_stream.id,
            "playback_id": live_stream.playback_id,
            "title": live_stream.title,
            "message": f"🔴 Live stream '{stream_data.title}' started",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await manager.broadcast_to_room(json.dumps(stream_message), room_id)
        
        return {
            "id": live_stream.id,
            "stream_key": live_stream.stream_key,
            "playback_id": live_stream.playback_id,
            "status": live_stream.status,
            "title": live_stream.title,
            "rtmp_url": "rtmp://global-live.mux.com:5222/live/"
        }
        
    except Exception as e:
        print(f"Mux API error: {e}")
        # Fallback to mock on error
        mock_stream_id = str(uuid.uuid4())
        mock_stream_key = f"mock_stream_key_{mock_stream_id[:8]}"
        mock_playback_id = f"mock_playback_{mock_stream_id[:8]}"
        
        live_stream = LiveStream(
            id=mock_stream_id,
            stream_key=mock_stream_key,
            playback_id=mock_playback_id,
            status="mock_ready",
            room_id=room_id,
            title=stream_data.title,
            created_at=datetime.utcnow()
        )
        live_streams[mock_stream_id] = live_stream
        
        return {
            "id": live_stream.id,
            "stream_key": live_stream.stream_key,
            "playback_id": live_stream.playback_id,
            "status": live_stream.status,
            "title": live_stream.title,
            "rtmp_url": "rtmp://mock-stream.example.com/live/",
            "note": f"Fallback to mock - Mux error: {str(e)}"
        }

@app.get("/rooms/{room_id}/live-streams")
def get_room_live_streams(room_id: str):
    """Get all live streams for a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_streams = [stream for stream in live_streams.values() if stream.room_id == room_id]
    return room_streams

@app.post("/rooms/{room_id}/video-upload")
async def create_video_upload(room_id: str, upload_data: VideoUploadCreate):
    """Create a video upload URL for a room using Mux API"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not mux_enabled:
        # Fallback to mock if Mux not available
        mock_upload_id = str(uuid.uuid4())
        mock_upload_url = f"https://mock-upload.example.com/{mock_upload_id}"
        
        video_upload = VideoUpload(
            id=mock_upload_id,
            upload_url=mock_upload_url,
            status="mock_ready",
            room_id=room_id,
            title=upload_data.title,
            created_at=datetime.utcnow()
        )
        video_uploads[mock_upload_id] = video_upload
        
        return {
            "id": video_upload.id,
            "upload_url": video_upload.upload_url,
            "status": video_upload.status,
            "title": video_upload.title,
            "note": "Mock implementation - Mux not configured"
        }
    
    try:
        # CORRECTED: Use proper mux-python 3.x API
        create_request = CreateDirectUploadRequest(
            new_asset_settings={
                "playback_policies": ["public"],
                "mp4_support": "standard"
            },
            cors_origin="*",
            test=False  # Set to False for production
        )
        
        # CORRECTED: Use correct API method
        upload_response = direct_uploads_api.create_direct_upload(create_request)
        
        # Store upload info
        video_upload = VideoUpload(
            id=upload_response.data.id,
            upload_url=upload_response.data.url,
            status="ready",
            room_id=room_id,
            title=upload_data.title,
            created_at=datetime.utcnow()
        )
        
        video_uploads[upload_response.data.id] = video_upload
        
        # Notify room about new video upload
        upload_message = {
            "type": "video_upload_created",
            "upload_id": video_upload.id,
            "upload_url": video_upload.upload_url,
            "title": video_upload.title,
            "message": f"📹 Video upload '{upload_data.title}' ready",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await manager.broadcast_to_room(json.dumps(upload_message), room_id)
        
        return {
            "id": video_upload.id,
            "upload_url": video_upload.upload_url,
            "status": video_upload.status,
            "title": video_upload.title
        }
        
    except Exception as e:
        print(f"Mux API error: {e}")
        # Fallback to mock on error
        mock_upload_id = str(uuid.uuid4())
        mock_upload_url = f"https://mock-upload.example.com/{mock_upload_id}"
        
        video_upload = VideoUpload(
            id=mock_upload_id,
            upload_url=mock_upload_url,
            status="mock_ready",
            room_id=room_id,
            title=upload_data.title,
            created_at=datetime.utcnow()
        )
        video_uploads[mock_upload_id] = video_upload
        
        return {
            "id": video_upload.id,
            "upload_url": video_upload.upload_url,
            "status": video_upload.status,
            "title": video_upload.title,
            "note": f"Fallback to mock - Mux error: {str(e)}"
        }

@app.get("/rooms/{room_id}/videos")
def get_room_videos(room_id: str):
    """Get all videos for a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_videos = [video for video in video_assets.values() if video["room_id"] == room_id]
    return room_videos

@app.post("/mux-webhook")
async def mux_webhook(request: dict):
    """Handle Mux webhooks for video processing updates"""
    try:
        event_type = request.get("type")
        data = request.get("data", {})
        
        if event_type == "video.asset.ready":
            # Asset is ready for playback
            asset_id = data.get("id")
            playback_ids = data.get("playback_ids", [])
            
            if playback_ids:
                playback_id = playback_ids[0].get("id")
                
                # Find the room for this asset
                for video in video_assets.values():
                    if video.get("asset_id") == asset_id:
                        room_id = video["room_id"]
                        
                        # Notify room about video ready
                        video_ready_message = {
                            "type": "video_ready",
                            "asset_id": asset_id,
                            "playback_id": playback_id,
                            "title": video["title"],
                            "message": f"🎥 Video '{video['title']}' is ready to watch",
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                        await manager.broadcast_to_room(json.dumps(video_ready_message), room_id)
                        break
        
        return {"status": "received"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}")

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    # More lenient validation - just check that user and room exist
    if room_id not in rooms:
        await websocket.close(code=4004, reason="Room not found")
        return
    if user_id not in users:
        await websocket.close(code=4004, reason="User not found")
        return
    
    # Add user to room if not already there (defensive programming)
    if user_id not in rooms[room_id].users:
        rooms[room_id].users.append(user_id)
    
    await manager.connect(websocket, room_id, user_id)
    user = users[user_id]
    
    # Notify room that user joined
    join_message = {
        "type": "user_joined",
        "message": f"{user.username} joined the chat",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    await manager.broadcast_to_room(json.dumps(join_message), room_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create message
            message_id = str(uuid.uuid4())
            message = Message(
                id=message_id,
                user_id=user_id,
                username=user.username,
                room_id=room_id,
                content=message_data["content"],
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            
            # Store message
            messages[room_id].append(message)
            
            # Broadcast message to room
            broadcast_data = {
                "type": "message",
                "id": message.id,
                "user_id": message.user_id,
                "username": message.username,
                "content": message.content,
                "timestamp": message.timestamp
            }
            await manager.broadcast_to_room(json.dumps(broadcast_data), room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, user_id)
        leave_message = {
            "type": "user_left",
            "message": f"{user.username} left the chat",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        await manager.broadcast_to_room(json.dumps(leave_message), room_id)

# Video-enhanced mobile-optimized chat interface with Mux integration
@app.get("/chat", response_class=HTMLResponse)
def get_chat_page():
    """Serve a comprehensive chat interface with Mux video capabilities"""
    html_content = """<!DOCTYPE html>
<html><head><title>FastAPI Chat with Video</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<script src="https://cdn.jsdelivr.net/npm/@mux/mux-player@1.0.0"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f5f5f5;height:100vh;display:flex;flex-direction:column}
.container{max-width:100%;margin:0;padding:10px;height:100%;display:flex;flex-direction:column}
.setup{background:white;padding:15px;border-radius:8px;margin-bottom:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.setup input,.setup button{width:100%;padding:12px;margin:5px 0;border:1px solid #ddd;border-radius:4px;font-size:16px}
.setup button{background:#007bff;color:white;border:none;cursor:pointer}
.setup button:hover{background:#0056b3}
.chat-interface{flex:1;display:none;flex-direction:column;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.chat-header{background:#007bff;color:white;padding:15px;font-weight:bold;display:flex;justify-content:space-between;align-items:center}
.video-controls{display:flex;gap:8px}
.video-controls button{padding:8px 12px;background:#28a745;color:white;border:none;border-radius:4px;cursor:pointer;font-size:12px}
.chat-area{flex:1;padding:10px;overflow-y:auto;background:#fafafa}
.message{margin:5px 0;padding:8px 12px;background:white;border-radius:8px;box-shadow:0 1px 2px rgba(0,0,0,0.1)}
.video-message{background:#e8f5e8;border-left:4px solid #28a745}
.live-stream-message{background:#fff3cd;border-left:4px solid #ffc107}
.system-message{background:#e3f2fd;color:#1976d2;font-style:italic}
.input-area{display:flex;padding:10px;background:#f8f9fa;border-top:1px solid #ddd}
.input-area input{flex:1;padding:12px;border:1px solid #ddd;border-radius:4px 0 0 4px;font-size:16px}
.input-area button{padding:12px 20px;border:1px solid #007bff;background:#007bff;color:white;border-radius:0 4px 4px 0;cursor:pointer}
.status{background:#d4edda;color:#155724;padding:10px;border-radius:4px;margin:10px 0;display:none}
.rooms-list{max-height:200px;overflow-y:auto}
.room-item{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #eee}
.room-item button{padding:6px 12px;background:#28a745;color:white;border:none;border-radius:4px;cursor:pointer}
.video-player{margin:10px 0;max-width:100%;height:300px}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);z-index:1000}
.modal-content{background:white;margin:10% auto;padding:20px;width:90%;max-width:500px;border-radius:8px}
.close{float:right;font-size:24px;cursor:pointer}
.video-upload{background:#f8f9fa;padding:15px;margin:10px 0;border-radius:8px;border:2px dashed #007bff}
.live-stream-info{background:#fff3cd;padding:10px;margin:10px 0;border-radius:4px;border:1px solid #ffeaa7}
@media (max-width:480px){.container{padding:5px}.setup{padding:10px}.chat-header{padding:10px}.input-area{padding:5px}.video-controls{flex-direction:column;gap:4px}.video-controls button{font-size:10px;padding:6px 8px}}
</style></head><body>
<div class="container">
<div id="setup" class="setup">
<h3>FastAPI Chat with Video</h3>
<input type="text" id="username" placeholder="Enter username" maxlength="20">
<button onclick="createUser()">Create User</button>
<input type="text" id="roomName" placeholder="Enter room name" maxlength="30">
<button onclick="createRoom()">Create Room</button>
<button onclick="loadRooms()">Load Rooms</button>
<div id="roomsList" class="rooms-list"></div>
</div>
<div id="chatInterface" class="chat-interface">
<div id="chatHeader" class="chat-header">
<span id="roomTitle">Chat Room</span>
<div class="video-controls">
<button onclick="startLiveStream()">🔴 Live</button>
<button onclick="uploadVideo()">📹 Upload</button>
</div>
</div>
<div id="chatArea" class="chat-area"></div>
<div class="input-area">
<input type="text" id="messageInput" placeholder="Type message..." maxlength="500" onkeypress="if(event.key==='Enter')sendMessage()">
<button onclick="sendMessage()">Send</button>
</div>
</div>
<div id="liveStreamModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeLiveStreamModal()">&times;</span>
<h3>Start Live Stream</h3>
<input type="text" id="streamTitle" placeholder="Stream title" style="width:100%;margin:10px 0;padding:10px;border:1px solid #ddd;border-radius:4px">
<button onclick="createLiveStream()" style="width:100%;padding:12px;background:#dc3545;color:white;border:none;border-radius:4px;cursor:pointer">Create Live Stream</button>
<div id="streamInfo" class="live-stream-info" style="display:none">
<h4>🔴 Stream Created!</h4>
<p><strong>Stream Key:</strong> <span id="streamKey"></span></p>
<p><strong>RTMP URL:</strong> rtmp://live.mux.com/live/</p>
<p><small>Use in OBS or streaming software</small></p>
</div>
</div>
</div>
<div id="videoUploadModal" class="modal">
<div class="modal-content">
<span class="close" onclick="closeVideoUploadModal()">&times;</span>
<h3>Upload Video</h3>
<input type="text" id="videoTitle" placeholder="Video title" style="width:100%;margin:10px 0;padding:10px;border:1px solid #ddd;border-radius:4px">
<input type="text" id="videoDescription" placeholder="Description (optional)" style="width:100%;margin:10px 0;padding:10px;border:1px solid #ddd;border-radius:4px">
<button onclick="createVideoUpload()" style="width:100%;padding:12px;background:#007bff;color:white;border:none;border-radius:4px;cursor:pointer">Get Upload URL</button>
<div id="uploadArea" class="video-upload" style="display:none">
<input type="file" id="videoFile" accept="video/*" style="margin:10px 0">
<button onclick="uploadVideoFile()" style="width:100%;padding:12px;background:#28a745;color:white;border:none;border-radius:4px;cursor:pointer">Upload Video</button>
<div id="uploadProgress" style="margin:10px 0"></div>
</div>
</div>
</div>
<div id="status" class="status"></div>
</div>
<script>
let ws=null,currentUser=null,currentRoom=null;
function startLiveStream(){document.getElementById('liveStreamModal').style.display='block'}
function closeLiveStreamModal(){document.getElementById('liveStreamModal').style.display='none'}
function uploadVideo(){document.getElementById('videoUploadModal').style.display='block'}
function closeVideoUploadModal(){document.getElementById('videoUploadModal').style.display='none'}
async function createLiveStream(){
if(!currentRoom){alert('Join a room first');return}
const title=document.getElementById('streamTitle').value.trim();
if(!title){alert('Enter stream title');return}
try{
const response=await fetch(`/rooms/${currentRoom.id}/live-stream`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title})});
if(response.ok){
const stream=await response.json();
document.getElementById('streamKey').textContent=stream.stream_key;
document.getElementById('streamInfo').style.display='block'}
else{alert('Failed to create live stream')}
}catch(error){alert('Error: '+error.message)}}
async function createVideoUpload(){
if(!currentRoom){alert('Join a room first');return}
const title=document.getElementById('videoTitle').value.trim();
const description=document.getElementById('videoDescription').value.trim();
if(!title){alert('Enter video title');return}
try{
const response=await fetch(`/rooms/${currentRoom.id}/video-upload`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,description})});
if(response.ok){
const upload=await response.json();
window.uploadUrl=upload.upload_url;
document.getElementById('uploadArea').style.display='block'}
else{alert('Failed to create upload URL')}
}catch(error){alert('Error: '+error.message)}}
async function uploadVideoFile(){
const fileInput=document.getElementById('videoFile');
const file=fileInput.files[0];
if(!file){alert('Select a video file');return}
if(!window.uploadUrl){alert('Create upload URL first');return}
const progressDiv=document.getElementById('uploadProgress');
progressDiv.innerHTML='Uploading...';
try{
const response=await fetch(window.uploadUrl,{method:'PUT',body:file,headers:{'Content-Type':file.type}});
if(response.ok){
progressDiv.innerHTML='Upload complete! Processing video...';
closeVideoUploadModal()}
else{progressDiv.innerHTML='Upload failed'}
}catch(error){progressDiv.innerHTML='Upload error: '+error.message}}
function displayMessage(data){
const chatArea=document.getElementById('chatArea');
const messageDiv=document.createElement('div');
if(data.type==='message'){
messageDiv.className='message';
const time=new Date(data.timestamp.endsWith('Z')?data.timestamp:data.timestamp+'Z').toLocaleTimeString();
messageDiv.innerHTML='<strong>'+data.username+'</strong> <small>('+time+')</small><br>'+data.content}
else if(data.type==='live_stream_created'){
messageDiv.className='message live-stream-message';
messageDiv.innerHTML='<strong>🔴 Live Stream Started</strong><br>'+data.message+'<br><mux-player playback-id="'+data.playback_id+'" metadata-video-title="'+data.title+'" controls class="video-player"></mux-player>'}
else if(data.type==='video_ready'){
messageDiv.className='message video-message';
messageDiv.innerHTML='<strong>🎥 Video Ready</strong><br>'+data.message+'<br><mux-player playback-id="'+data.playback_id+'" metadata-video-title="'+data.title+'" controls class="video-player"></mux-player>'}
else{messageDiv.className='message system-message';messageDiv.textContent=data.message}
chatArea.appendChild(messageDiv);chatArea.scrollTop=chatArea.scrollHeight}
async function createUser(){
const username=document.getElementById('username').value.trim();
if(!username){alert('Enter username');return}
try{
const response=await fetch('/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username})});
if(response.ok){currentUser=await response.json();showStatus('User created: '+currentUser.username)}
else{alert('Failed to create user')}
}catch(error){alert('Error: '+error.message)}}
async function createRoom(){
const roomName=document.getElementById('roomName').value.trim();
if(!roomName){alert('Enter room name');return}
try{
const response=await fetch('/rooms',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:roomName})});
if(response.ok){showStatus('Room created');loadRooms()}
else{alert('Failed to create room')}
}catch(error){alert('Error: '+error.message)}}
async function loadRooms(){
try{
const response=await fetch('/rooms');
const rooms=await response.json();
const roomsList=document.getElementById('roomsList');
roomsList.innerHTML='<h4>Rooms:</h4>';
rooms.forEach(room=>{
const roomDiv=document.createElement('div');
roomDiv.className='room-item';
roomDiv.innerHTML='<span>'+room.name+'</span><button onclick="joinRoom(\''+room.id+'\',\''+room.name+'\')">Join</button>';
roomsList.appendChild(roomDiv)})
}catch(error){alert('Error loading rooms')}}
async function joinRoom(roomId,roomName){
if(!currentUser){alert('Create user first');return}
currentRoom={id:roomId,name:roomName};
try{
await fetch('/rooms/'+roomId+'/join',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:currentUser.id})})
}catch(error){console.error('Error joining room:',error)}
const wsUrl=(window.location.protocol==='https:'?'wss://':'ws://')+window.location.host+'/ws/'+roomId+'/'+currentUser.id;
ws=new WebSocket(wsUrl);
ws.onopen=function(){
document.getElementById('setup').style.display='none';
document.getElementById('chatInterface').style.display='flex';
document.getElementById('roomTitle').textContent='Room: '+roomName;
showStatus('Connected');
loadMessages()};
ws.onmessage=function(event){displayMessage(JSON.parse(event.data))};
ws.onclose=function(){showStatus('Disconnected')};
ws.onerror=function(){showStatus('Connection error')}}
async function loadMessages(){
try{
const response=await fetch('/rooms/'+currentRoom.id+'/messages');
const messages=await response.json();
const chatArea=document.getElementById('chatArea');
chatArea.innerHTML='';
messages.forEach(message=>{displayMessage({type:'message',username:message.username,content:message.content,timestamp:message.timestamp})})}
catch(error){console.error('Error loading messages')}}
function sendMessage(){
const messageInput=document.getElementById('messageInput');
const content=messageInput.value.trim();
if(!content||!ws)return;
ws.send(JSON.stringify({content}));messageInput.value=''}
function showStatus(message){
const status=document.getElementById('status');
status.textContent=message;status.style.display='block';
setTimeout(()=>status.style.display='none',3000)}
window.onload=loadRooms;
</script></body></html>"""
    return html_content