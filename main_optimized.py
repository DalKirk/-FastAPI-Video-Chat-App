"""
Cleaned optimized FastAPI application.
Serves a canonical static chat UI from static/chat.html and provides basic
WebSocket-backed chat functionality with a ConnectionManager.
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Bunny.net optional config
BUNNY_API_KEY = os.getenv("BUNNY_API_KEY")
BUNNY_LIBRARY_ID = os.getenv("BUNNY_LIBRARY_ID")
BUNNY_PULL_ZONE = os.getenv("BUNNY_PULL_ZONE")
BUNNY_COLLECTION_ID = os.getenv("BUNNY_COLLECTION_ID", "")

bunny_enabled = bool(BUNNY_API_KEY and BUNNY_LIBRARY_ID and BUNNY_PULL_ZONE)
if bunny_enabled:
  logger.info("Bunny.net Stream configured")
else:
  logger.info("Bunny.net not configured - video features disabled")


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


class LiveStream(BaseModel):
  id: str
  stream_key: str
  playback_id: str
  status: str
  room_id: str
  title: str
  created_at: datetime


# In-memory stores
rooms: Dict[str, Room] = {}
messages: Dict[str, List[Message]] = {}
users: Dict[str, User] = {}
live_streams: Dict[str, LiveStream] = {}
video_assets: Dict[str, dict] = {}
video_uploads: Dict[str, VideoUpload] = {}


# Connection manager
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
    if room_id in self.active_connections and websocket in self.active_connections[room_id]:
      try:
        self.active_connections[room_id].remove(websocket)
      except ValueError:
        pass
    if user_id in self.user_connections:
      try:
        del self.user_connections[user_id]
      except KeyError:
        pass

  async def send_personal_message(self, message: str, websocket: WebSocket):
    await websocket.send_text(message)

  async def broadcast_to_room(self, message: str, room_id: str):
    if room_id not in self.active_connections:
      return
    connections = list(self.active_connections[room_id])
    dead = []
    for conn in connections:
      try:
        await conn.send_text(message)
      except Exception:
        dead.append(conn)
    for d in dead:
      if d in self.active_connections.get(room_id, []):
        try:
          self.active_connections[room_id].remove(d)
        except ValueError:
          pass


manager = ConnectionManager()


# App and CORS (make origins configurable via ALLOWED_ORIGINS env var)
app = FastAPI(title="FastAPI Video Chat", description="Real-time messaging with WebSocket support")

# Recommended default origins (add your Vercel frontend(s) here)
default_frontend_origins = [
  "http://localhost:3000",
  "http://127.0.0.1:3000",
  "http://192.168.1.119:3000",
  "https://video-chat-frontend-ruby.vercel.app",
  "https://next-js-14-front-end-for-chat-plast.vercel.app",
]

# Allow overriding via comma-separated environment variable ALLOWED_ORIGINS
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
  allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]
  logger.info(f"Using ALLOWED_ORIGINS from env: {allowed_origins}")
else:
  allowed_origins = default_frontend_origins.copy()
  logger.info(f"Using default allowed origins: {allowed_origins}")

# For local development convenience, you can include '*' via env or when not in production
if os.getenv("ENVIRONMENT") != "production" and "*" not in allowed_origins:
  allowed_origins.append("*")

app.add_middleware(
  CORSMiddleware,
  allow_origins=allowed_origins,
  allow_credentials=True,
  allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allow_headers=["*"],
)


# Basic endpoints
@app.get("/")
def root():
  return {"message": "FastAPI Video Chat API is running", "bunny_enabled": bunny_enabled}


@app.get("/health")
def health():
  return {"status": "ok", "time": datetime.utcnow().isoformat() + "Z"}


@app.post("/users")
def create_user(user: UserCreate):
  user_id = str(uuid.uuid4())
  new_user = User(id=user_id, username=user.username, joined_at=datetime.utcnow())
  users[user_id] = new_user
  return new_user


@app.get("/users")
def get_users():
  return list(users.values())


@app.post("/rooms")
def create_room(room: RoomCreate):
  room_id = str(uuid.uuid4())
  new_room = Room(id=room_id, name=room.name, created_at=datetime.utcnow(), users=[])
  rooms[room_id] = new_room
  messages[room_id] = []
  return new_room


@app.get("/rooms")
def get_rooms():
  return list(rooms.values())


@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, payload: JoinRoomRequest):
  if room_id not in rooms:
    raise HTTPException(status_code=404, detail="Room not found")
  if payload.user_id not in users:
    raise HTTPException(status_code=404, detail="User not found")
  if payload.user_id not in rooms[room_id].users:
    rooms[room_id].users.append(payload.user_id)
  return {"message": "joined"}


@app.get("/rooms/{room_id}/messages")
def get_room_messages(room_id: str):
  if room_id not in rooms:
    raise HTTPException(status_code=404, detail="Room not found")
  return messages.get(room_id, [])


# WebSocket endpoint
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
      payload = json.loads(data)
      message_id = str(uuid.uuid4())
      msg = Message(id=message_id, user_id=user_id, username=user.username, room_id=room_id, content=payload.get("content", ""), timestamp=datetime.utcnow().isoformat() + "Z")
      messages[room_id].append(msg)
      broadcast = {"type": "message", "id": msg.id, "user_id": msg.user_id, "username": msg.username, "content": msg.content, "timestamp": msg.timestamp}
      await manager.broadcast_to_room(json.dumps(broadcast), room_id)
  except WebSocketDisconnect:
    manager.disconnect(websocket, room_id, user_id)
    leave_message = {"type": "user_left", "message": f"{user.username} left the chat", "timestamp": datetime.utcnow().isoformat() + "Z"}
    await manager.broadcast_to_room(json.dumps(leave_message), room_id)


# Serve the canonical static chat UI
@app.get("/chat", response_class=HTMLResponse)
def get_chat_page():
  static_path = os.path.join(os.path.dirname(__file__), "static", "chat.html")
  if os.path.exists(static_path):
    return FileResponse(static_path, media_type="text/html")
  return HTMLResponse("<html><body><h3>Chat UI not found. Please create static/chat.html</h3></body></html>")
