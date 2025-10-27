"""
FastAPI Video Chat Application - Optimized for Railway Deployment
Real-time messaging with WebSocket support and Bunny.net Stream integration
"""

import os
import json
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from urllib.parse import parse_qs

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator, ConfigDict
from middleware.rate_limit import RateLimitMiddleware, RateLimitConfig

from utils.streaming_ai_endpoints import streaming_ai_router
from api.routes.chat import router as chat_router

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bunny.net configuration
BUNNY_API_KEY = os.getenv("BUNNY_API_KEY")
BUNNY_LIBRARY_ID = os.getenv("BUNNY_LIBRARY_ID")
BUNNY_PULL_ZONE = os.getenv("BUNNY_PULL_ZONE")
BUNNY_COLLECTION_ID = os.getenv("BUNNY_COLLECTION_ID", "")
bunny_enabled = all([BUNNY_API_KEY, BUNNY_LIBRARY_ID, BUNNY_PULL_ZONE])

# Deployment behavior toggles (safer defaults for production stateless environments)
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
AUTO_CREATE_ON_WS_CONNECT = os.getenv("ALLOW_WEBSOCKET_AUTO_ROOMS", "true" if ENVIRONMENT == "production" else "false").lower() == "true"
AUTO_CREATE_ON_JOIN = os.getenv("ALLOW_JOIN_AUTO_ROOMS", "true" if ENVIRONMENT == "production" else "false").lower() == "true"
AUTO_USER_ON_JOIN = os.getenv("ALLOW_JOIN_AUTO_USERS", "true" if ENVIRONMENT == "production" else "false").lower() == "true"

# Data Models
class User(BaseModel):
    id: str
    username: str
    joined_at: datetime

    @field_validator('username')
    @classmethod
    def username_must_be_valid(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Username must be at least 2 characters long')
        return v.strip()

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
    users: List[str] = Field(default_factory=list)
    model_config = ConfigDict(arbitrary_types_allowed=True)

class UserCreate(BaseModel):
    username: str

class RoomCreate(BaseModel):
    name: str

class JoinRoomRequest(BaseModel):
    user_id: str
    username: Optional[str] = None  # optional fallback for stateless envs

# In-memory storage
rooms: Dict[str, Room] = {}
messages: Dict[str, List[Message]] = {}
users: Dict[str, User] = {}
# In-memory storage for simple video/live-stream features used by tests
room_live_streams: Dict[str, List[Dict]] = {}
room_videos: Dict[str, List[Dict]] = {}

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        try:
            await websocket.accept()
            if room_id not in self.active_connections:
                self.active_connections[room_id] = []
            self.active_connections[room_id].append(websocket)
            self.user_connections[user_id] = websocket
            logger.info(f"User {user_id} connected to room {room_id}")
        except Exception as e:
            logger.error(f"Failed to connect websocket for user {user_id}: {e}")
            raise

    def disconnect(self, websocket: WebSocket, room_id: str, user_id: str):
        try:
            if room_id in self.active_connections:
                if websocket in self.active_connections[room_id]:
                    self.active_connections[room_id].remove(websocket)
            if user_id in self.user_connections:
                del self.user_connections[user_id]
            logger.info(f"User {user_id} disconnected from room {room_id}")
        except Exception as e:
            logger.error(f"Error during disconnect for user {user_id}: {e}")

    async def broadcast_to_room(self, message: str, room_id: str):
        if room_id not in self.active_connections:
            return

        connections = self.active_connections[room_id].copy()
        dead_connections = []

        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.warning(f"Failed to send message to connection: {e}")
                dead_connections.append(connection)

        for dead_connection in dead_connections:
            if dead_connection in self.active_connections[room_id]:
                self.active_connections[room_id].remove(dead_connection)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting FastAPI Video Chat Application")
    logger.info(f"Bunny.net Stream: {'enabled' if bunny_enabled else 'disabled'}")
    try:
        yield
    finally:
        logger.info("🛑 Shutting down FastAPI Video Chat Application")

app = FastAPI(
    title="FastAPI Video Chat",
    description="Real-time messaging with WebSocket support",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://localhost:3000",
    "https://next-js-14-front-end-for-chat-plast.vercel.app",
    "https://next-js-14-front-end-for-chat-plast-kappa.vercel.app",
    "https://video-chat-frontend-ruby.vercel.app",
]

if os.getenv("ENVIRONMENT") != "production":
    cors_allow_origins = []
    cors_allow_origin_regex = r".*"
else:
    cors_allow_origins = allowed_origins
    cors_allow_origin_regex = r"https://.*\.vercel\.app"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_origin_regex=cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

# Rate limiting
per_endpoint_limits = {
    "/api/v1/chat": RateLimitConfig(requests_limit=20, time_window=60),
}

app.add_middleware(
    RateLimitMiddleware,
    requests_limit=100,
    time_window=60,
    per_endpoint_limits=per_endpoint_limits,
    exclude_paths={"/health", "/", "/docs", "/openapi.json", "/redoc", "/_debug", "/debug", "/api/_debug", "/api/debug"},
)

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "600",
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(streaming_ai_router)
app.include_router(chat_router)

@app.get("/ai/health")
async def ai_health_redirect():
    from api.routes.chat import chat_health_check
    return await chat_health_check()

@app.post("/api/ai-proxy")
async def ai_proxy(request: Request):
    try:
        from api.routes.chat import chat_endpoint, get_ai_service
        ai_service = get_ai_service()
        return await chat_endpoint(request, ai_service)
    except Exception as e:
        logger.error(f"AI proxy error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

manager = ConnectionManager()

@app.get("/")
def root():
    return {
        "message": "FastAPI Video Chat API is running!",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "chat": "/chat",
        "bunny_stream": "enabled" if bunny_enabled else "disabled"
    }

@app.get("/_debug")
async def debug_info():
    """Lightweight debug endpoint used by tests."""
    return {
        "bunny_enabled": bunny_enabled,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "has_rooms": len(rooms) > 0,
        "has_users": len(users) > 0,
        "auto_create_on_ws": AUTO_CREATE_ON_WS_CONNECT,
        "auto_create_on_join": AUTO_CREATE_ON_JOIN,
        "auto_user_on_join": AUTO_USER_ON_JOIN,
    }

# Additional aliases so debug works behind proxies or API prefixes
@app.get("/debug")
async def debug_info_alias():
    return await debug_info()

@app.get("/api/_debug")
async def debug_info_api_prefixed():
    return await debug_info()

@app.get("/api/debug")
async def debug_info_api_alias():
    return await debug_info()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "services": {
            "api": "running",
            "websocket": "running",
            "bunny_stream": "enabled" if bunny_enabled else "disabled"
        },
        "stats": {
            "active_rooms": len(rooms),
            "active_users": len(users),
            "total_messages": sum(len(msgs) for msgs in messages.values())
        }
    }

@app.post("/users", response_model=User)
def create_user(user_data: UserCreate):
    username = user_data.username.strip() if user_data.username else ""
    if not username or len(username) < 2:
        raise HTTPException(status_code=422, detail="Username must be at least 2 characters long")
    
    user_id = str(uuid.uuid4())
    user = User(id=user_id, username=username, joined_at=datetime.now(timezone.utc))
    users[user_id] = user
    logger.info(f"Created user: {user.username} ({user_id})")
    return user

@app.get("/users", response_model=List[User])
def get_users():
    return list(users.values())

@app.post("/rooms", response_model=Room)
def create_room(room_data: RoomCreate):
    room_id = str(uuid.uuid4())
    room = Room(id=room_id, name=room_data.name, created_at=datetime.now(timezone.utc))
    rooms[room_id] = room
    messages[room_id] = []
    # initialize containers for room assets
    room_live_streams.setdefault(room_id, [])
    room_videos.setdefault(room_id, [])
    logger.info(f"Created room: {room.name} ({room_id})")
    return room

@app.get("/rooms", response_model=List[Room])
def get_rooms():
    return list(rooms.values())

@app.get("/rooms/{room_id}", response_model=Room)
def get_room(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_id]

@app.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str, limit: int = 50):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    room_messages = messages.get(room_id, [])
    return [{
        "id": msg.id,
        "user_id": msg.user_id,
        "username": msg.username,
        "room_id": msg.room_id,
        "content": msg.content,
        "timestamp": msg.timestamp
    } for msg in room_messages[-limit:]]

@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, join_data: JoinRoomRequest):
    # Optionally auto-create a room in production/stateless envs
    if room_id not in rooms:
        if AUTO_CREATE_ON_JOIN:
            room = Room(id=room_id, name=f"Room {room_id[:8]}", created_at=datetime.now(timezone.utc))
            rooms[room_id] = room
            messages.setdefault(room_id, [])
            room_live_streams.setdefault(room_id, [])
            room_videos.setdefault(room_id, [])
            logger.info(f"Auto-created room during join: {room_id}")
        else:
            raise HTTPException(status_code=404, detail="Room not found")

    # Optionally auto-create user if not found and username provided
    if join_data.user_id not in users:
        if AUTO_USER_ON_JOIN and join_data.username:
            # Create user using provided id to preserve client state
            user = User(id=join_data.user_id, username=join_data.username.strip(), joined_at=datetime.now(timezone.utc))
            users[join_data.user_id] = user
            logger.info(f"Auto-created user during join: {user.username} ({user.id})")
        else:
            raise HTTPException(status_code=404, detail="User not found")

    if join_data.user_id not in rooms[room_id].users:
        rooms[room_id].users.append(join_data.user_id)
        logger.info(f"User {users[join_data.user_id].username} joined room {rooms[room_id].name}")

    return {"message": f"User {users[join_data.user_id].username} joined room {rooms[room_id].name}"}

# --- Video/Live Stream Endpoints (simple in-memory mock) ---
@app.post("/rooms/{room_id}/live-stream")
async def create_live_stream(room_id: str, request: Request):
    """Create a mock live stream for a room.
    If Bunny is configured, this could be extended to call their API.
    """
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")

    payload = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    title = (payload.get("title") or "Live Stream").strip()

    stream_id = f"stream-{uuid.uuid4()}"
    stream_key = f"key-{uuid.uuid4().hex[:16]}"
    stream_info = {
        "id": stream_id,
        "title": title,
        "stream_key": stream_key,
        "created_at": datetime.now(timezone.utc).isoformat() + "Z",
    }

    room_live_streams.setdefault(room_id, []).append(stream_info)
    return stream_info

@app.get("/rooms/{room_id}/live-streams")
async def list_live_streams(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return room_live_streams.get(room_id, [])

@app.get("/rooms/{room_id}/videos")
async def list_room_videos(room_id: str):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return room_videos.get(room_id, [])

# WebSocket endpoint
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    # Optionally auto-create missing room in production/stateless envs
    if room_id not in rooms:
        if AUTO_CREATE_ON_WS_CONNECT:
            room = Room(id=room_id, name=f"Room {room_id[:8]}", created_at=datetime.now(timezone.utc))
            rooms[room_id] = room
            messages.setdefault(room_id, [])
            room_live_streams.setdefault(room_id, [])
            room_videos.setdefault(room_id, [])
            logger.info(f"Auto-created room during websocket connect: {room_id}")
        else:
            await websocket.close(code=4004, reason="Room not found")
            return

    # If user isn't known, allow providing username via query string to auto-create in prod
    if user_id not in users:
        try:
            qs = parse_qs(websocket.scope.get("query_string", b"").decode())
        except Exception:
            qs = {}
        provided_username = None
        if isinstance(qs, dict):
            values = qs.get("username")
            if values:
                provided_username = values[0]
        if ENVIRONMENT == "production" and provided_username and len(provided_username.strip()) >= 2:
            user = User(id=user_id, username=provided_username.strip(), joined_at=datetime.now(timezone.utc))
            users[user_id] = user
            logger.info(f"Auto-created user during websocket connect: {user.username} ({user.id})")
        else:
            await websocket.close(code=4004, reason="User not found")
            return

    if user_id not in rooms[room_id].users:
        rooms[room_id].users.append(user_id)

    await manager.connect(websocket, room_id, user_id)
    user = users[user_id]

    join_message = {
        "type": "user_joined",
        "message": f"{user.username} joined the chat",
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
    }
    await manager.broadcast_to_room(json.dumps(join_message), room_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if not isinstance(message_data, dict) or "content" not in message_data:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid message format"}))
                continue

            message_id = str(uuid.uuid4())
            message = Message(
                id=message_id,
                user_id=user_id,
                username=user.username,
                room_id=room_id,
                content=message_data["content"].strip(),
                timestamp=datetime.now(timezone.utc).isoformat() + "Z"
            )

            messages[room_id].append(message)

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
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z"
        }
        await manager.broadcast_to_room(json.dumps(leave_message), room_id)
        logger.info(f"WebSocket disconnected for user {user.username}")

    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(websocket, room_id, user_id)

# Chat HTML
@app.get("/chat", response_class=HTMLResponse)
def get_chat_page():
    return """<!DOCTYPE html>
<html><head><title>FastAPI Video Chat</title><meta charset="UTF-8">
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f5f5f5;height:100vh;display:flex;flex-direction:column}.container{max-width:100%;margin:0;padding:10px;height:100%;display:flex;flex-direction:column}.setup{background:white;padding:15px;border-radius:8px;margin-bottom:10px}.setup input,.setup button{width:100%;padding:12px;margin:5px 0;border:1px solid #ddd;border-radius:4px}.setup button{background:#007bff;color:white;border:none;cursor:pointer}.chat-interface{flex:1;display:none;flex-direction:column;background:white;border-radius:8px;overflow:hidden}.chat-header{background:#007bff;color:white;padding:15px;font-weight:bold}.chat-area{flex:1;padding:10px;overflow-y:auto;background:#fafafa}.message{margin:5px 0;padding:8px 12px;background:white;border-radius:8px}.system-message{background:#e3f2fd;color:#1976d2;font-style:italic}.input-area{display:flex;padding:10px;background:#f8f9fa}.input-area input{flex:1;padding:12px;border:1px solid #ddd;border-radius:4px 0 0 4px}.input-area button{padding:12px 20px;background:#007bff;color:white;border:none;border-radius:0 4px 4px 0;cursor:pointer}.rooms-list{max-height:200px;overflow-y:auto}.room-item{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #eee}.room-item button{padding:6px 12px;background:#28a745;color:white;border:none;border-radius:4px;cursor:pointer}</style></head><body>
<div class="container">
<div id="setup" class="setup">
<h3>FastAPI Video Chat</h3>
<input type="text" id="username" placeholder="Enter username">
<button onclick="createUser()">Create User</button>
<input type="text" id="roomName" placeholder="Enter room name">
<button onclick="createRoom()">Create Room</button>
<button onclick="loadRooms()">Load Rooms</button>
<div id="roomsList" class="rooms-list"></div>
</div>
<div id="chatInterface" class="chat-interface">
<div class="chat-header"><span id="roomTitle">Chat Room</span></div>
<div id="chatArea" class="chat-area"></div>
<div class="input-area">
<input type="text" id="messageInput" placeholder="Type message..." onkeypress="if(event.key==='Enter')sendMessage()">
<button onclick="sendMessage()">Send</button>
</div>
</div>
</div>
<script>
let ws=null,currentUser=null,currentRoom=null;
async function createUser(){
const username=document.getElementById('username').value.trim();
if(!username){alert('Enter username');return}
const response=await fetch('/users',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username})});
if(response.ok){currentUser=await response.json();alert('User created: '+currentUser.username)}}
async function createRoom(){
const roomName=document.getElementById('roomName').value.trim();
if(!roomName){alert('Enter room name');return}
const response=await fetch('/rooms',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:roomName})});
if(response.ok){loadRooms()}}
async function loadRooms(){
const response=await fetch('/rooms');
const rooms=await response.json();
const roomsList=document.getElementById('roomsList');
roomsList.innerHTML='<h4>Rooms:</h4>';
rooms.forEach(room=>{
const roomDiv=document.createElement('div');
roomDiv.className='room-item';
roomDiv.innerHTML='<span>'+room.name+'</span><button onclick="joinRoom(\\''+room.id+'\\',\\''+room.name+'\\')">Join</button>';
roomsList.appendChild(roomDiv)})}
async function joinRoom(roomId,roomName){
if(!currentUser){alert('Create user first');return}
currentRoom={id:roomId,name:roomName};
const wsProto=window.location.protocol==='https:'?'wss:':'ws:';
const wsUrl=wsProto+'//'+window.location.host+'/ws/'+roomId+'/'+currentUser.id;
ws=new WebSocket(wsUrl);
ws.onopen=function(){
document.getElementById('setup').style.display='none';
document.getElementById('chatInterface').style.display='flex';
document.getElementById('roomTitle').textContent='Room: '+roomName;
loadMessages()};
ws.onmessage=function(event){displayMessage(JSON.parse(event.data))};
ws.onerror=function(){alert('Connection error')}}
async function loadMessages(){
const response=await fetch('/rooms/'+currentRoom.id+'/messages');
const messages=await response.json();
const chatArea=document.getElementById('chatArea');
chatArea.innerHTML='';
messages.forEach(msg=>{displayMessage({type:'message',username:msg.username,content:msg.content,timestamp:msg.timestamp})})}
function displayMessage(data){
const chatArea=document.getElementById('chatArea');
const messageDiv=document.createElement('div');
if(data.type==='message'){
messageDiv.className='message';
messageDiv.innerHTML='<strong>'+data.username+'</strong><br>'+data.content}
else{messageDiv.className='message system-message';messageDiv.textContent=data.message}
chatArea.appendChild(messageDiv);
chatArea.scrollTop=chatArea.scrollHeight}
function sendMessage(){
const messageInput=document.getElementById('messageInput');
const content=messageInput.value.trim();
if(!content||!ws)return;
ws.send(JSON.stringify({content}));messageInput.value=''
}
window.onload=loadRooms;
</script></body></html>"""

@app.get("/websocket-demo", response_class=HTMLResponse)
def get_websocket_demo():
    try:
        with open("websocket_demo.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Demo page not found</h1></body></html>"

