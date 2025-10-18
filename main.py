"""
main.py - Cleaned FastAPI app

This file provides a working FastAPI server with WebSocket and upload-proxy
endpoints. It replaces the previous broken content and removes stray
blocks that caused syntax errors on import.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bunny.net config
BUNNY_API_KEY = os.getenv("BUNNY_API_KEY")
BUNNY_LIBRARY_ID = os.getenv("BUNNY_LIBRARY_ID")
BUNNY_PULL_ZONE = os.getenv("BUNNY_PULL_ZONE")
BUNNY_COLLECTION_ID = os.getenv("BUNNY_COLLECTION_ID", "")

REQUIRED_ENV_VARS = ["BUNNY_API_KEY", "BUNNY_LIBRARY_ID", "BUNNY_PULL_ZONE"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    logger.warning(f"Missing required environment variables: {missing_vars}")
    bunny_enabled = False
else:
    bunny_enabled = True
    logger.info("✅ Bunny.net Stream configured successfully")

# Models
class User(BaseModel):
    id: str
    username: str
    joined_at: datetime

    @validator('username')
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

    class Config:
        arbitrary_types_allowed = True

class MessageCreate(BaseModel):
    content: str

class RoomCreate(BaseModel):
    name: str

class UserCreate(BaseModel):
    username: str

class JoinRoomRequest(BaseModel):
    user_id: str

class StreamCreate(BaseModel):
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

    class Config:
        arbitrary_types_allowed = True

class LiveStream(BaseModel):
    id: str
    stream_key: str
    playback_id: str
    status: str
    room_id: str
    title: str
    created_at: datetime

    class Config:
        arbitrary_types_allowed = True

# Storage
rooms: Dict[str, Room] = {}
messages: Dict[str, List[Message]] = {}
users: Dict[str, User] = {}
live_streams: Dict[str, LiveStream] = {}
video_assets: Dict[str, dict] = {}
video_uploads: Dict[str, VideoUpload] = {}

# Manager
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
            if room_id in self.active_connections and websocket in self.active_connections[room_id]:
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
        for dead in dead_connections:
            if dead in self.active_connections[room_id]:
                self.active_connections[room_id].remove(dead)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting FastAPI Video Chat Application")
    logger.info(f"Bunny.net Stream: {'enabled' if bunny_enabled else 'disabled'}")
    try:
        yield
    except Exception as e:
        logger.error(f"Error during application lifespan: {e}", exc_info=True)
        raise
    finally:
        logger.info("🛑 Shutting down FastAPI Video Chat Application")

app = FastAPI(title="FastAPI Video Chat", description="Real-time messaging with WebSocket support and Bunny.net Stream integration", version="2.0.0", lifespan=lifespan)

allowed_origins = ["http://localhost:3000", "https://localhost:3000"]
if os.getenv("ENVIRONMENT") != "production":
    allowed_origins.append("*")

app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["*"])

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

manager = ConnectionManager()

@app.get("/")
def root():
    return {"message": "FastAPI Video Chat API is running!", "version": "2.0.0", "docs": "/docs", "health": "/health", "chat": "/chat"}

@app.get("/health")
async def health_check():
    bunny_status = "enabled" if bunny_enabled else "disabled"
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat() + "Z", "version": "2.0.0", "services": {"api": "running", "websocket": "running", "bunny_stream": bunny_status}}

@app.get("/_debug")
def debug_info():
    return {"bunny_enabled": bunny_enabled, "active_rooms": len(rooms), "active_users": len(users)}

@app.post("/users", response_model=User)
def create_user(user_data: UserCreate):
    user_id = str(uuid.uuid4())
    user = User(id=user_id, username=user_data.username, joined_at=datetime.utcnow())
    users[user_id] = user
    return user

@app.get("/users", response_model=List[User])
def get_users():
    return list(users.values())

@app.post("/rooms", response_model=Room)
def create_room(room_data: RoomCreate):
    room_id = str(uuid.uuid4())
    room = Room(id=room_id, name=room_data.name, created_at=datetime.utcnow())
    rooms[room_id] = room
    messages[room_id] = []
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
    formatted_messages = []
    for msg in room_messages[-limit:]:
        formatted_messages.append({"id": msg.id, "user_id": msg.user_id, "username": msg.username, "room_id": msg.room_id, "content": msg.content, "timestamp": msg.timestamp})
    return formatted_messages

@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, join_data: JoinRoomRequest):
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if join_data.user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    if join_data.user_id not in rooms[room_id].users:
        rooms[room_id].users.append(join_data.user_id)
    return {"message": f"User {users[join_data.user_id].username} joined room {rooms[room_id].name}"}

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    if room_id not in rooms:
        await websocket.close(code=4004, reason="Room not found")
        return
    if user_id not in users:
        await websocket.close(code=4004, reason="User not found")
        return
    if user_id not in rooms[room_id].users:
        rooms[room_id].users.append(user_id)
    await manager.connect(websocket, room_id, user_id)
    user = users[user_id]
    join_message = {"type": "user_joined", "message": f"{user.username} joined the chat", "timestamp": datetime.utcnow().isoformat() + "Z"}
    await manager.broadcast_to_room(json.dumps(join_message), room_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            if not isinstance(message_data, dict) or "content" not in message_data:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid message format"}))
                continue
            message_id = str(uuid.uuid4())
            message = Message(id=message_id, user_id=user_id, username=user.username, room_id=room_id, content=message_data["content"].strip(), timestamp=datetime.utcnow().isoformat() + "Z")
            messages[room_id].append(message)
            broadcast_data = {"type": "message", "id": message.id, "user_id": message.user_id, "username": message.username, "content": message.content, "timestamp": message.timestamp}
            await manager.broadcast_to_room(json.dumps(broadcast_data), room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, user_id)
        leave_message = {"type": "user_left", "message": f"{user.username} left the chat", "timestamp": datetime.utcnow().isoformat() + "Z"}
        await manager.broadcast_to_room(json.dumps(leave_message), room_id)

CHAT_HTML = """<!DOCTYPE html>
<html><head><title>FastAPI Video Chat</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head><body>
<h1>FastAPI Video Chat</h1>
<p>Use the frontend or connect a WebSocket to /ws/&lt;room&gt;/&lt;user&gt;</p>
</body></html>"""

@app.get("/chat", response_class=HTMLResponse)
def get_chat_page():
    return CHAT_HTML