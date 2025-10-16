from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import json
import uuid

app = FastAPI(title="Chat API", description="Real-time messaging API with WebSocket support")

# Add CORS middleware for mobile browser compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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
    timestamp: datetime

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

# In-memory storage (in production, use a database)
rooms: Dict[str, Room] = {}
messages: Dict[str, List[Message]] = {}
users: Dict[str, User] = {}

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
            for connection in self.active_connections[room_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove dead connections
                    self.active_connections[room_id].remove(connection)

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
        joined_at=datetime.now()
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
        created_at=datetime.now()
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

@app.get("/rooms/{room_id}/messages", response_model=List[Message])
def get_room_messages(room_id: str, limit: int = 50):
    """Get messages from a room"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    room_messages = messages.get(room_id, [])
    return room_messages[-limit:]  # Return last N messages

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
        "message": f"{user.username} joined the chat",
        "timestamp": datetime.now().isoformat()
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
                timestamp=datetime.now()
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
                "timestamp": message.timestamp.isoformat()
            }
            await manager.broadcast_to_room(json.dumps(broadcast_data), room_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id, user_id)
        leave_message = {
            "type": "user_left",
            "message": f"{user.username} left the chat",
            "timestamp": datetime.now().isoformat()
        }
        await manager.broadcast_to_room(json.dumps(leave_message), room_id)

# Lightweight mobile-optimized chat interface
@app.get("/chat", response_class=HTMLResponse)
def get_chat_page():
    """Serve a lightweight mobile-optimized chat interface"""
    html_content = """<!DOCTYPE html>
<html><head><title>FastAPI Chat</title><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Arial,sans-serif;background:#f5f5f5;height:100vh;display:flex;flex-direction:column}
.container{max-width:100%;margin:0;padding:10px;height:100%;display:flex;flex-direction:column}
.setup{background:white;padding:15px;border-radius:8px;margin-bottom:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.setup input,.setup button{width:100%;padding:12px;margin:5px 0;border:1px solid #ddd;border-radius:4px;font-size:16px}
.setup button{background:#007bff;color:white;border:none;cursor:pointer}
.setup button:hover{background:#0056b3}
.chat-interface{flex:1;display:none;flex-direction:column;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1)}
.chat-header{background:#007bff;color:white;padding:15px;font-weight:bold}
.chat-area{flex:1;padding:10px;overflow-y:auto;background:#fafafa}
.message{margin:5px 0;padding:8px 12px;background:white;border-radius:8px;box-shadow:0 1px 2px rgba(0,0,0,0.1)}
.system-message{background:#e3f2fd;color:#1976d2;font-style:italic}
.input-area{display:flex;padding:10px;background:#f8f9fa;border-top:1px solid #ddd}
.input-area input{flex:1;padding:12px;border:1px solid #ddd;border-radius:4px 0 0 4px;font-size:16px}
.input-area button{padding:12px 20px;border:1px solid #007bff;background:#007bff;color:white;border-radius:0 4px 4px 0;cursor:pointer}
.status{background:#d4edda;color:#155724;padding:10px;border-radius:4px;margin:10px 0;display:none}
.rooms-list{max-height:200px;overflow-y:auto}
.room-item{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #eee}
.room-item button{padding:6px 12px;background:#28a745;color:white;border:none;border-radius:4px;cursor:pointer}
@media (max-width:480px){.container{padding:5px}.setup{padding:10px}.chat-header{padding:10px}.input-area{padding:5px}}
</style></head><body>
<div class="container">
<div id="setup" class="setup">
<h3>FastAPI Chat</h3>
<input type="text" id="username" placeholder="Enter username" maxlength="20">
<button onclick="createUser()">Create User</button>
<input type="text" id="roomName" placeholder="Enter room name" maxlength="30">
<button onclick="createRoom()">Create Room</button>
<button onclick="loadRooms()">Load Rooms</button>
<div id="roomsList" class="rooms-list"></div>
</div>
<div id="chatInterface" class="chat-interface">
<div id="chatHeader" class="chat-header">Chat Room</div>
<div id="chatArea" class="chat-area"></div>
<div class="input-area">
<input type="text" id="messageInput" placeholder="Type message..." maxlength="500" onkeypress="if(event.key==='Enter')sendMessage()">
<button onclick="sendMessage()">Send</button>
</div>
</div>
<div id="status" class="status"></div>
</div>
<script>
let ws=null,currentUser=null,currentRoom=null;
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
const wsUrl='ws://'+window.location.host+'/ws/'+roomId+'/'+currentUser.id;
ws=new WebSocket(wsUrl);
ws.onopen=function(){
document.getElementById('setup').style.display='none';
document.getElementById('chatInterface').style.display='flex';
document.getElementById('chatHeader').textContent='Room: '+roomName;
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
function displayMessage(data){
const chatArea=document.getElementById('chatArea');
const messageDiv=document.createElement('div');
if(data.type==='message'){
messageDiv.className='message';
const time=new Date(data.timestamp).toLocaleTimeString();
messageDiv.innerHTML='<strong>'+data.username+'</strong> <small>('+time+')</small><br>'+data.content}
else{messageDiv.className='message system-message';messageDiv.textContent=data.message}
chatArea.appendChild(messageDiv);chatArea.scrollTop=chatArea.scrollHeight}
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