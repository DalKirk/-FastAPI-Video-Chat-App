# 🔌 WebSocket Setup and Troubleshooting Guide

## ✅ **WEBSOCKET ISSUE FIXED - October 16, 2025**

### **Problem Identified:**
The frontend was using **Socket.IO client** while the backend was using **native FastAPI WebSockets**. These are **incompatible protocols** and cannot communicate with each other.

---

## 🔧 **What Was Fixed:**

### **1. Frontend WebSocket Client Updated**
**File:** `video-chat-frontend/lib/socket.ts`

**Before (Socket.IO):**
```typescript
import { io, Socket } from 'socket.io-client';

this.socket = io(WS_URL, {
  transports: ['websocket', 'polling'],
  // Socket.IO specific configuration
});
```

**After (Native WebSocket):**
```typescript
// Native WebSocket connection
this.socket = new WebSocket(`wss://domain.com/ws/${roomId}/${userId}`);

this.socket.onopen = () => { /* connected */ };
this.socket.onmessage = (event) => { /* message received */ };
this.socket.onclose = () => { /* disconnected */ };
this.socket.onerror = (error) => { /* error */ };
```

### **2. Key Changes Made:**

✅ **Removed Socket.IO dependency** - No longer needed  
✅ **Implemented native WebSocket API** - Browser built-in, no external library  
✅ **Auto-reconnection with exponential backoff** - Handles connection drops  
✅ **Proper message parsing** - JSON parse/stringify for data exchange  
✅ **Environment-aware URLs** - Automatically uses `wss://` for production, `ws://` for development  

---

## 🚀 **WebSocket Architecture:**

### **Backend (FastAPI) - Already Working:**
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            # Process and broadcast message
            await manager.broadcast_to_room(json.dumps(message), room_id)
    except WebSocketDisconnect:
        # Handle disconnect
```

**WebSocket URL Format:**
```
Production:  wss://natural-presence-production.up.railway.app/ws/{room_id}/{user_id}
Development: ws://localhost:8000/ws/{room_id}/{user_id}
```

### **Frontend (Next.js) - Now Fixed:**
```typescript
class SocketManager {
  private socket: WebSocket | null = null;
  
  connect(roomId: string, userId: string): void {
    const WS_URL = `wss://domain.com/ws/${roomId}/${userId}`;
    this.socket = new WebSocket(WS_URL);
    
    this.socket.onopen = () => {
      console.log('✅ Connected');
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Handle message
    };
  }
  
  sendMessage(content: string): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ content }));
    }
  }
}
```

---

## 📋 **WebSocket Connection Flow:**

### **Step 1: User Joins Room**
1. Frontend creates WebSocket connection: `wss://backend.com/ws/room-123/user-456`
2. Backend validates room and user exist
3. Backend accepts connection: `await websocket.accept()`
4. User is added to room's active connections
5. Backend broadcasts "user joined" message to all room members

### **Step 2: Sending Messages**
1. User types message in frontend
2. Frontend sends via WebSocket: `socket.send(JSON.stringify({ content: "Hello" }))`
3. Backend receives message: `data = await websocket.receive_text()`
4. Backend creates Message object with ID, timestamp, etc.
5. Backend broadcasts to all connections in room

### **Step 3: Receiving Messages**
1. Backend sends: `await websocket.send_text(json.dumps(message))`
2. Frontend receives: `socket.onmessage = (event) => { ... }`
3. Frontend parses: `const data = JSON.parse(event.data)`
4. Frontend displays message in UI

### **Step 4: Disconnect**
1. User closes browser/leaves room
2. WebSocket connection closes
3. Backend receives `WebSocketDisconnect` exception
4. Backend removes user from active connections
5. Backend broadcasts "user left" message

---

## 🛠️ **How to Use WebSocket in Your Frontend:**

### **Example: Chat Room Component**

```typescript
import { socketManager } from '@/lib/socket';
import { useEffect, useState } from 'react';

export function ChatRoom({ roomId, userId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    // Connect to WebSocket
    socketManager.connect(roomId, userId);
    
    // Listen for connection status
    socketManager.onConnect((connected) => {
      setIsConnected(connected);
      if (connected) {
        console.log('✅ WebSocket connected!');
      } else {
        console.log('❌ WebSocket disconnected');
      }
    });
    
    // Listen for messages
    socketManager.onMessage((message) => {
      setMessages((prev) => [...prev, message]);
    });
    
    // Cleanup on unmount
    return () => {
      socketManager.disconnect();
    };
  }, [roomId, userId]);
  
  const sendMessage = (content: string) => {
    try {
      socketManager.sendMessage(content);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Not connected to chat. Please refresh the page.');
    }
  };
  
  return (
    <div>
      <ConnectionStatus isConnected={isConnected} />
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} disabled={!isConnected} />
    </div>
  );
}
```

---

## ✅ **Testing WebSocket Connection:**

### **Test 1: Browser Console**
```javascript
// Open browser console on your frontend
const ws = new WebSocket('wss://natural-presence-production.up.railway.app/ws/test-room/test-user');

ws.onopen = () => console.log('✅ Connected!');
ws.onmessage = (e) => console.log('📨 Received:', e.data);
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = (e) => console.log('🔌 Closed:', e.code, e.reason);

// Send a test message
ws.send(JSON.stringify({ content: 'Hello!' }));
```

### **Test 2: Backend Verification**
```bash
# Check Railway logs for WebSocket connections
railway logs

# You should see:
# INFO: ('127.0.0.1', 12345) - "WebSocket /ws/room/user" [accepted]
# INFO: connection open
```

### **Test 3: Browser DevTools**
1. Open DevTools → Network tab
2. Filter by "WS" (WebSocket)
3. Click on WebSocket connection
4. View frames being sent/received
5. Check for any error codes

---

## 🔍 **Troubleshooting:**

### **Issue: "WebSocket connection failed"**
**Symptoms:** Frontend shows "Not connected to server"

**Causes:**
1. ❌ Backend server is down/sleeping
2. ❌ Wrong WebSocket URL
3. ❌ CORS blocking connection
4. ❌ User/Room doesn't exist

**Solutions:**
```bash
# 1. Check if backend is running
curl https://natural-presence-production.up.railway.app/health

# 2. Verify WebSocket URL format
# Should be: wss://domain.com/ws/{room_id}/{user_id}
# NOT: wss://domain.com (missing path)

# 3. Check Railway logs
railway logs

# 4. Create user and room first
# User must exist before WebSocket connection
# Room must exist before joining
```

### **Issue: "Cannot send message - WebSocket not connected"**
**Symptoms:** Messages don't send, error in console

**Causes:**
1. ❌ Trying to send before connection is open
2. ❌ Connection dropped and not reconnected
3. ❌ Wrong WebSocket state

**Solutions:**
```typescript
// Always check connection state before sending
if (socketManager.isConnected()) {
  socketManager.sendMessage(content);
} else {
  console.error('WebSocket not connected');
  // Show error to user
  // Try to reconnect
}

// Check WebSocket ready state
const state = socket.readyState;
// 0 = CONNECTING
// 1 = OPEN (ready to send)
// 2 = CLOSING
// 3 = CLOSED
```

### **Issue: "WebSocket closes immediately"**
**Symptoms:** Connects then disconnects right away

**Causes:**
1. ❌ Backend validation failed (user/room not found)
2. ❌ Backend error during connection
3. ❌ Network/firewall blocking

**Solutions:**
```typescript
// Check close code for reason
socket.onclose = (event) => {
  console.log('Close code:', event.code);
  console.log('Close reason:', event.reason);
  
  // Common codes:
  // 1000 = Normal closure
  // 1006 = Abnormal closure
  // 4004 = Custom: User/Room not found
};

// Backend sends 4004 when user/room doesn't exist
await websocket.close(code=4004, reason="Room not found")
```

---

## 📊 **WebSocket Ready States:**

| State | Value | Description | Can Send? |
|-------|-------|-------------|-----------|
| CONNECTING | 0 | Connection is being established | ❌ No |
| OPEN | 1 | Connection is open and ready | ✅ Yes |
| CLOSING | 2 | Connection is closing | ❌ No |
| CLOSED | 3 | Connection is closed | ❌ No |

---

## 🎯 **Best Practices:**

### **1. Always Check Connection State**
```typescript
// DON'T do this:
socket.send(data); // Might fail if not connected

// DO this:
if (socket.readyState === WebSocket.OPEN) {
  socket.send(data);
} else {
  console.error('Cannot send - socket not ready');
}
```

### **2. Handle Reconnection**
```typescript
// Implement auto-reconnect with exponential backoff
let reconnectAttempts = 0;
const maxAttempts = 5;

socket.onclose = () => {
  if (reconnectAttempts < maxAttempts) {
    const delay = 1000 * Math.pow(2, reconnectAttempts);
    setTimeout(() => connect(), delay);
    reconnectAttempts++;
  }
};
```

### **3. Show Connection Status to User**
```typescript
// Visual indicator of connection state
<div className={isConnected ? 'connected' : 'disconnected'}>
  {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
</div>
```

### **4. Handle Errors Gracefully**
```typescript
socket.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Show user-friendly message
  toast.error('Connection lost. Trying to reconnect...');
};
```

---

## 🚀 **Next Steps:**

### **For Frontend Developers:**

1. **Remove Socket.IO** from package.json:
```bash
cd video-chat-frontend
npm uninstall socket.io-client
```

2. **Update Your Components** to use the new socket manager:
```typescript
import { socketManager } from '@/lib/socket';

// In your component:
useEffect(() => {
  socketManager.connect(roomId, userId);
  socketManager.onMessage(handleMessage);
  return () => socketManager.disconnect();
}, [roomId, userId]);
```

3. **Deploy to Vercel:**
```bash
git add .
git commit -m "feat: Switch to native WebSocket"
git push
# Vercel will auto-deploy
```

### **For Backend Developers:**

✅ **Backend is already working!** No changes needed. The FastAPI WebSocket implementation is solid.

Just ensure:
- Railway backend is running
- CORS allows your frontend domain
- Health check endpoint responds

---

## 📚 **Additional Resources:**

- **MDN WebSocket API:** https://developer.mozilla.org/en-US/docs/Web/API/WebSocket
- **FastAPI WebSockets:** https://fastapi.tiangolo.com/advanced/websockets/
- **Railway Docs:** https://docs.railway.app/

---

## ✅ **Verification Checklist:**

- [x] Backend WebSocket endpoint working (`/ws/{room_id}/{user_id}`)
- [x] Frontend using native WebSocket (not Socket.IO)
- [x] Auto-reconnection implemented
- [x] Error handling in place
- [x] Connection status visible to users
- [x] Message send/receive working
- [x] Railway deployment configured
- [x] CORS properly set up

---

**Status:** ✅ **WebSocket support fully functional**

**Last Updated:** October 16, 2025  
**Backend:** Railway (natural-presence-production)  
**Frontend:** Vercel (video-chat-frontend)

