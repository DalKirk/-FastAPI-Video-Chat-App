from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid
import os
from pydantic import BaseModel

app = FastAPI(title="Chat API", description="Real-time messaging API with WebSocket support")

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://next-js-14-front-end-for-chat-plast.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        FRONTEND_URL,
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Data Models
class User(BaseModel):
    id: str
    username: str

class Message(BaseModel):
    id: str
    user_id: str
    username: str
    content: str
    timestamp: datetime
    room_id: str

class CreateUserRequest(BaseModel):
    username: str

class JoinRoomRequest(BaseModel):
    room_id: str

class SendMessageRequest(BaseModel):
    content: str
    room_id: str

# In-memory storage
rooms: Dict[str, dict] = {}
messages: Dict[str, List[dict]] = {}
users: Dict[str, dict] = {}

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

manager = ConnectionManager()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment verification"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "api": "running",
            "websocket": "running"
        }
    }

# API Endpoints
@app.get("/")
def root():
    return {"message": "FastAPI Chat API is running! Visit /chat for the chat interface or /docs for API documentation."}

@app.post("/users")
def create_user(user_data: dict):
    """Create a new user"""
    username = user_data.get("username")
    if not username:
        raise HTTPException(status_code=400, detail="Username required")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "username": username,
        "joined_at": datetime.now().isoformat()
    }
    users[user_id] = user
    return user

@app.get("/users")
def get_users():
    """Get all users"""
    return list(users.values())

@app.post("/rooms")
def create_room(room_data: dict):
    """Create a new chat room"""
    name = room_data.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Room name required")
    
    room_id = str(uuid.uuid4())
    room = {
        "id": room_id,
        "name": name,
        "created_at": datetime.now().isoformat(),
        "users": []
    }
    rooms[room_id] = room
    messages[room_id] = []
    return room

@app.get("/rooms")
def get_rooms():
    """Get all chat rooms"""
    return list(rooms.values())

@app.get("/rooms/{room_id}")
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
    return room_messages[-limit:]

@app.post("/rooms/{room_id}/join")
def join_room(room_id: str, join_data: dict):
    """Join a room"""
    user_id = join_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID required")
    
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_id not in rooms[room_id]["users"]:
        rooms[room_id]["users"].append(user_id)
    
    return {"message": f"User {users[user_id]['username']} joined room {rooms[room_id]['name']}"}

# WebSocket endpoint for real-time chat
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    if room_id not in rooms:
        await websocket.close(code=4004, reason="Room not found")
        return
    if user_id not in users:
        await websocket.close(code=4004, reason="User not found")
        return
    
    await manager.connect(websocket, room_id, user_id)
    user = users[user_id]
    
    # Notify room that user joined
    join_message = {
        "type": "user_joined",
        "message": f"{user['username']} joined the chat",
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_room(json.dumps(join_message), room_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                print(f"Received message data: {message_data}")
                
                # Validate message format
                if "content" not in message_data:
                    print("Error: Missing 'content' field in message")
                    continue
                
                # Create message
                message_id = str(uuid.uuid4())
                message = {
                    "id": message_id,
                    "user_id": user_id,
                    "username": user["username"],
                    "room_id": room_id,
                    "content": message_data["content"],
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"Created message: {message}")
                
                # Store message
                if room_id not in messages:
                    print(f"Warning: messages[{room_id}] not initialized, initializing now")
                    messages[room_id] = []
                
                messages[room_id].append(message)
                print(f"Message stored successfully. Total messages in room: {len(messages[room_id])}")
                
                # Broadcast message to room
                broadcast_data = {
                    "type": "message",
                    "id": message["id"],
                    "user_id": message["user_id"],
                    "username": message["username"],
                    "content": message["content"],
                    "timestamp": message["timestamp"]
                }
                
                print(f"Broadcasting message: {broadcast_data}")
                await manager.broadcast_to_room(json.dumps(broadcast_data), room_id)
                print("Message broadcast successful")
                
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                continue
            except KeyError as e:
                print(f"Key error in message processing: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error in message processing: {e}")
                continue
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for user {user_id} in room {room_id}")
        manager.disconnect(websocket, room_id, user_id)
        leave_message = {
            "type": "user_left",
            "message": f"{user['username']} left the chat",
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast_to_room(json.dumps(leave_message), room_id)

# Chat interface
@app.get("/chat", response_class=HTMLResponse)
def get_chat_page():
    """Serve chat interface"""
    return """<!DOCTYPE html>
<html>
<head>
    <title>FastAPI Chat</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; }
        .setup { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .setup h2 { color: #333; margin-bottom: 20px; }
        .setup input, .setup button { width: 100%; padding: 12px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; box-sizing: border-box; }
        .setup button { background: #007bff; color: white; border: none; cursor: pointer; font-weight: bold; }
        .setup button:hover { background: #0056b3; }
        .chat { background: white; border-radius: 8px; overflow: hidden; display: none; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .chat-header { background: #007bff; color: white; padding: 15px; font-weight: bold; }
        .chat-area { height: 300px; overflow-y: auto; padding: 15px; background: #fafafa; }
        .message { margin: 8px 0; padding: 10px; background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .system-message { background: #e3f2fd; color: #1976d2; font-style: italic; text-align: center; }
        .input-area { display: flex; padding: 15px; background: white; border-top: 1px solid #eee; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 4px 0 0 4px; font-size: 16px; }
        .input-area button { padding: 12px 20px; background: #007bff; color: white; border: 1px solid #007bff; border-radius: 0 4px 4px 0; cursor: pointer; font-weight: bold; }
        .input-area button:hover { background: #0056b3; }
        .status { padding: 12px; background: #d4edda; color: #155724; margin: 10px 0; border-radius: 4px; display: none; border: 1px solid #c3e6cb; }
        .room-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #eee; }
        .room-item button { padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; width: auto; margin: 0; }
        .room-item button:hover { background: #218838; }
        #roomsList { margin-top: 15px; }
        #roomsList h4 { color: #333; margin-bottom: 10px; }
        .sound-controls { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; border: 1px solid #ddd; }
        .sound-controls label { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .sound-controls input[type="checkbox"] { margin: 0; }
        .sound-controls input[type="range"] { flex: 1; margin-left: 10px; }
        .volume-label { font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div id="setup" class="setup">
            <h2>FastAPI Chat</h2>
            <div class="sound-controls">
                <label>
                    <input type="checkbox" id="soundEnabled" checked>
                    🔊 Enable Sound Notifications
                </label>
                <div style="display: flex; align-items: center; margin-top: 5px;">
                    <span class="volume-label">Volume:</span>
                    <input type="range" id="volumeControl" min="0" max="100" value="50">
                    <span class="volume-label" id="volumeDisplay">50%</span>
                </div>
            </div>
            <input type="text" id="username" placeholder="Enter your username">
            <button type="button" onclick="createUser()">Create User</button>
            <input type="text" id="roomName" placeholder="Enter room name">
            <button type="button" onclick="createRoom()">Create Room</button>
            <button type="button" onclick="loadRooms()">Load Rooms</button>
            <div id="roomsList"></div>
        </div>
        
        <div id="chat" class="chat">
            <div id="chatHeader" class="chat-header">Chat Room</div>
            <div id="chatArea" class="chat-area"></div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Type your message...">
                <button type="button" onclick="sendMessage()">Send</button>
            </div>
        </div>
        
        <div id="status" class="status"></div>
    </div>

    <script>
        let ws = null;
        let currentUser = null;
        let currentRoom = null;

        // Sound system
        class SoundManager {
            constructor() {
                this.enabled = true;
                this.volume = 0.5;
                this.sounds = {};
                this.initializeSounds();
            }

            initializeSounds() {
                // Create sound effects using Web Audio API
                this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
                
                // Define sound frequencies and patterns
                this.soundTypes = {
                    message: { frequency: 800, duration: 0.15, type: 'sine' },
                    userJoined: { frequency: 600, duration: 0.3, type: 'triangle' },
                    userLeft: { frequency: 400, duration: 0.3, type: 'triangle' },
                    connected: { frequency: 1000, duration: 0.2, type: 'square' },
                    error: { frequency: 300, duration: 0.5, type: 'sawtooth' },
                    notification: { frequency: 900, duration: 0.1, type: 'sine' }
                };
            }

            async playSound(type) {
                if (!this.enabled || !this.soundTypes[type]) return;
                
                try {
                    // Resume audio context if suspended (browser policy)
                    if (this.audioContext.state === 'suspended') {
                        await this.audioContext.resume();
                    }

                    const { frequency, duration, type: waveType } = this.soundTypes[type];
                    
                    // Create oscillator
                    const oscillator = this.audioContext.createOscillator();
                    const gainNode = this.audioContext.createGain();
                    
                    oscillator.connect(gainNode);
                    gainNode.connect(this.audioContext.destination);
                    
                    oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
                    oscillator.type = waveType;
                    
                    // Set volume with fade out
                    gainNode.gain.setValueAtTime(this.volume * 0.3, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
                    
                    oscillator.start(this.audioContext.currentTime);
                    oscillator.stop(this.audioContext.currentTime + duration);
                    
                } catch (error) {
                    console.log('Sound playback failed:', error);
                }
            }

            setEnabled(enabled) {
                this.enabled = enabled;
            }

            setVolume(volume) {
                this.volume = volume / 100;
            }
        }

        // Initialize sound manager
        const soundManager = new SoundManager();

        function showStatus(message, isError = false) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.style.display = 'block';
            status.style.background = isError ? '#f8d7da' : '#d4edda';
            status.style.color = isError ? '#721c24' : '#155724';
            status.style.borderColor = isError ? '#f5c6cb' : '#c3e6cb';
            setTimeout(() => status.style.display = 'none', 3000);
            console.log('Status:', message);
        }

        async function createUser() {
            console.log('createUser function called');
            const username = document.getElementById('username').value.trim();
            console.log('Username input value:', username);
            
            if (!username) { 
                showStatus('Please enter a username', true); 
                return; 
            }
            
            try {
                console.log('Making API call to create user');
                const response = await fetch('/users', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username: username})
                });
                
                console.log('API response status:', response.status);
                
                if (response.ok) {
                    currentUser = await response.json();
                    showStatus('User created: ' + currentUser.username);
                    soundManager.playSound('notification');
                    console.log('User created successfully:', currentUser);
                } else {
                    const errorText = await response.text();
                    showStatus('Failed to create user: ' + errorText, true);
                    console.error('Create user failed:', errorText);
                }
            } catch (error) {
                showStatus('Error creating user: ' + error.message, true);
                console.error('Create user error:', error);
            }
        }

        async function createRoom() {
            console.log('createRoom function called');
            const roomName = document.getElementById('roomName').value.trim();
            console.log('Room name input value:', roomName);
            
            if (!roomName) { 
                showStatus('Please enter a room name', true); 
                return; 
            }
            
            try {
                console.log('Making API call to create room');
                const response = await fetch('/rooms', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({name: roomName})
                });
                
                console.log('API response status:', response.status);
                
                if (response.ok) {
                    const room = await response.json();
                    showStatus('Room created: ' + room.name);
                    soundManager.playSound('notification');
                    console.log('Room created successfully:', room);
                    document.getElementById('roomName').value = '';
                    loadRooms();
                } else {
                    const errorText = await response.text();
                    showStatus('Failed to create room: ' + errorText, true);
                    console.error('Create room failed:', errorText);
                }
            } catch (error) {
                showStatus('Error creating room: ' + error.message, true);
                console.error('Create room error:', error);
            }
        }

        async function loadRooms() {
            console.log('loadRooms function called');
            try {
                const response = await fetch('/rooms');
                console.log('Load rooms API response status:', response.status);
                
                if (response.ok) {
                    const rooms = await response.json();
                    console.log('Rooms loaded:', rooms);
                    
                    const roomsList = document.getElementById('roomsList');
                    roomsList.innerHTML = '<h4>Available Rooms:</h4>';
                    
                    if (rooms.length === 0) {
                        roomsList.innerHTML += '<p>No rooms available. Create one!</p>';
                    } else {
                        rooms.forEach(room => {
                            const roomDiv = document.createElement('div');
                            roomDiv.className = 'room-item';
                            roomDiv.innerHTML = `<span><strong>${room.name}</strong></span><button onclick="joinRoom('${room.id}', '${room.name}')">Join</button>`;
                            roomsList.appendChild(roomDiv);
                        });
                    }
                } else {
                    const errorText = await response.text();
                    showStatus('Failed to load rooms: ' + errorText, true);
                    console.error('Load rooms failed:', errorText);
                }
            } catch (error) {
                showStatus('Error loading rooms: ' + error.message, true);
                console.error('Load rooms error:', error);
            }
        }

        async function joinRoom(roomId, roomName) {
            console.log('joinRoom function called with:', roomId, roomName);
            if (!currentUser) { 
                showStatus('Please create a user first', true); 
                return; 
            }
            
            currentRoom = {id: roomId, name: roomName};
            
            try {
                const response = await fetch(`/rooms/${roomId}/join`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({user_id: currentUser.id})
                });
                
                console.log('Join room API response status:', response.status);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    showStatus('Failed to join room: ' + errorText, true);
                    return;
                }
            } catch (error) {
                console.error('Join room error:', error);
            }
            
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/${roomId}/${currentUser.id}`;
            console.log('Connecting to WebSocket:', wsUrl);
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected successfully');
                document.getElementById('setup').style.display = 'none';
                document.getElementById('chat').style.display = 'block';
                document.getElementById('chatHeader').textContent = 'Room: ' + roomName;
                showStatus('Connected to ' + roomName);
                soundManager.playSound('connected');
            };
            
            ws.onmessage = function(event) {
                console.log('WebSocket message received:', event.data);
                const data = JSON.parse(event.data);
                displayMessage(data);
                
                // Play appropriate sound based on message type
                if (data.type === 'message') {
                    soundManager.playSound('message');
                } else if (data.type === 'user_joined') {
                    soundManager.playSound('userJoined');
                } else if (data.type === 'user_left') {
                    soundManager.playSound('userLeft');
                }
            };
            
            ws.onclose = function(event) {
                console.log('WebSocket closed:', event.code, event.reason);
                showStatus('Disconnected from room', true);
                soundManager.playSound('error');
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
                showStatus('Connection error', true);
                soundManager.playSound('error');
            };
        }

        function displayMessage(data) {
            const chatArea = document.getElementById('chatArea');
            const messageDiv = document.createElement('div');
            
            if (data.type === 'message') {
                messageDiv.className = 'message';
                const time = new Date(data.timestamp).toLocaleTimeString();
                messageDiv.innerHTML = `<strong>${data.username}</strong> <small>(${time})</small><br>${data.content}`;
            } else {
                messageDiv.className = 'message system-message';
                messageDiv.textContent = data.message;
            }
            
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
            
            // Add visual notification effect for new messages
            if (data.type === 'message') {
                messageDiv.style.backgroundColor = '#e8f5e8';
                setTimeout(() => {
                    messageDiv.style.backgroundColor = 'white';
                }, 1000);
            }
        }

        function sendMessage() {
            console.log('sendMessage function called');
            const messageInput = document.getElementById('messageInput');
            const content = messageInput.value.trim();
            console.log('Message content:', content);
            
            if (!content) {
                showStatus('Please enter a message', true);
                return;
            }
            
            if (!ws) {
                showStatus('Not connected to a room', true);
                return;
            }
            
            console.log('Sending WebSocket message:', content);
            ws.send(JSON.stringify({content: content}));
            messageInput.value = '';
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Page loaded, setting up event listeners');
            
            // Sound control event listeners
            const soundToggle = document.getElementById('soundEnabled');
            const volumeControl = document.getElementById('volumeControl');
            const volumeDisplay = document.getElementById('volumeDisplay');
            
            soundToggle.addEventListener('change', function() {
                soundManager.setEnabled(this.checked);
                if (this.checked) {
                    soundManager.playSound('notification');
                }
            });
            
            volumeControl.addEventListener('input', function() {
                const volume = parseInt(this.value);
                soundManager.setVolume(volume);
                volumeDisplay.textContent = volume + '%';
            });
            
            // Enter key support for message input
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
            }
            
            // Enter key support for username input
            const usernameInput = document.getElementById('username');
            if (usernameInput) {
                usernameInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        createUser();
                    }
                });
            }
            
            // Enter key support for room name input
            const roomNameInput = document.getElementById('roomName');
            if (roomNameInput) {
                roomNameInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        createRoom();
                    }
                });
            }
            
            // Load rooms on page load
            loadRooms();
            console.log('Initialization complete');
        });
    </script>
</body>
</html>"""

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)