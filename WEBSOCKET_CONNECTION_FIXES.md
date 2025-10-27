# ?? WebSocket Connection Issues - Complete Fix Guide

## ?? Problem: Chat Rooms Won't Connect

### Common Symptoms:
- ? WebSocket connection fails immediately
- ? "Room not found" or "User not found" errors
- ? Connection closes with code 4004
- ? Frontend shows "Connection error" or "Failed to connect"

---

## ?? Root Causes Identified

### 1. **User/Room Must Exist Before WebSocket Connection**

**The Issue:**
Your `main.py` (lines 296-309) requires users and rooms to exist BEFORE connecting to WebSocket:

```python
if room_id not in rooms:
    if AUTO_CREATE_ON_WS_CONNECT:  # Only true in production
        # Auto-create room
    else:
        await websocket.close(code=4004, reason="Room not found")
        return
```

**In Development:** `AUTO_CREATE_ON_WS_CONNECT = false` by default
**In Production:** Can be enabled via environment variable

### 2. **Environment Configuration Missing**

Check your `.env` file or Railway environment variables:

**Missing/Incorrect:**
```bash
ENVIRONMENT=development  # This disables auto-creation!
```

**Should be (for production):**
```bash
ENVIRONMENT=production
ALLOW_WEBSOCKET_AUTO_ROOMS=true
ALLOW_JOIN_AUTO_ROOMS=true
ALLOW_JOIN_AUTO_USERS=true
```

### 3. **Incorrect Connection Flow**

**Wrong Order (?):**
```javascript
// Connect to WebSocket first
const ws = new WebSocket(`wss://backend.com/ws/${roomId}/${userId}`);
// Then try to create user/room - TOO LATE!
```

**Correct Order (?):**
```javascript
// 1. Create user first
const user = await fetch('/users', { method: 'POST', body: JSON.stringify({ username: 'test' }) });

// 2. Create room
const room = await fetch('/rooms', { method: 'POST', body: JSON.stringify({ name: 'test room' }) });

// 3. Join room (optional but recommended)
await fetch(`/rooms/${room.id}/join`, { method: 'POST', body: JSON.stringify({ user_id: user.id }) });

// 4. NOW connect WebSocket
const ws = new WebSocket(`wss://backend.com/ws/${room.id}/${user.id}`);
```

---

## ? Solution Options

### **Option 1: Fix Frontend Connection Flow (Recommended)**

Update your frontend to create users/rooms BEFORE WebSocket connection:

**Example Fix for `static/chat.html` or similar:**

```javascript
async function joinRoom(roomId, roomName) {
  if (!currentUser) {
    alert('Create user first');
    return;
  }

  // ? IMPORTANT: Join room via HTTP API first
  try {
    const joinResponse = await fetch(`/rooms/${roomId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        user_id: currentUser.id,
        username: currentUser.username  // Include username for fallback
      })
    });

    if (!joinResponse.ok) {
      const error = await joinResponse.json();
      alert(`Failed to join room: ${error.detail}`);
      return;
    }
  } catch (error) {
    console.error('Error joining room:', error);
    alert('Failed to join room');
    return;
  }

  // ? NOW connect WebSocket
  currentRoom = { id: roomId, name: roomName };
  const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${wsProto}//${window.location.host}/ws/${roomId}/${currentUser.id}`;
  
  ws = new WebSocket(wsUrl);
  
  ws.onopen = function() {
    console.log('? WebSocket connected');
    document.getElementById('setup').style.display = 'none';
    document.getElementById('chatInterface').style.display = 'flex';
    document.getElementById('roomTitle').textContent = 'Room: ' + roomName;
    loadMessages();
  };
  
  ws.onerror = function(error) {
    console.error('? WebSocket error:', error);
    alert('Connection error - check console');
  };
  
  ws.onclose = function(event) {
    console.log('WebSocket closed:', event.code, event.reason);
    if (event.code === 4004) {
      alert('Room or user not found. Please create them first.');
    }
  };
}
```

### **Option 2: Enable Auto-Creation in Production**

Set these environment variables in Railway:

```bash
ENVIRONMENT=production
ALLOW_WEBSOCKET_AUTO_ROOMS=true
ALLOW_JOIN_AUTO_ROOMS=true
ALLOW_JOIN_AUTO_USERS=true
```

**?? Warning:** This is less secure but more convenient for development/testing.

### **Option 3: Modify Backend to Always Auto-Create (Development)**

Edit `main.py` line 28-30:

**Current:**
```python
AUTO_CREATE_ON_WS_CONNECT = os.getenv("ALLOW_WEBSOCKET_AUTO_ROOMS", "true" if ENVIRONMENT == "production" else "false").lower() == "true"
```

**Change to:**
```python
AUTO_CREATE_ON_WS_CONNECT = os.getenv("ALLOW_WEBSOCKET_AUTO_ROOMS", "true").lower() == "true"
```

This enables auto-creation in both development and production.

---

## ?? Testing the Fix

### **Test 1: Local Server**

```bash
# Start server
python -m uvicorn main:app --reload --port 8000

# In another terminal, run test
python test_websocket_simple.py
```

**Expected Output:**
```
? User created: test_user
? Room created: test_room
? WebSocket connected successfully
? Join message: test_user joined the chat
? Message broadcast received
?? ALL TESTS PASSED!
```

### **Test 2: Network-Level Test**

```bash
# Make sure server is running first
python tools/ws_network_smoke.py
```

### **Test 3: Browser Test**

1. Open `http://localhost:8000/chat`
2. Create a user (enter username, click "Create User")
3. Create a room (enter room name, click "Create Room")
4. Click "Load Rooms"
5. Click "Join" on the room
6. **This should now connect successfully**

---

## ?? Debugging Checklist

### If WebSocket Still Fails:

**1. Check Server Logs:**
```bash
# Look for these messages:
INFO: User {user_id} connected to room {room_id}
# or
WARNING: WebSocket closed with code 4004: Room not found
```

**2. Check Browser Console:**
```javascript
// Open DevTools (F12) and look for:
WebSocket connection to 'ws://localhost:8000/ws/...' failed
// Or
WebSocket closed: code 4004, reason: "User not found"
```

**3. Verify User/Room Exist:**
```bash
# Check if user exists
curl http://localhost:8000/users

# Check if room exists
curl http://localhost:8000/rooms

# Check specific room
curl http://localhost:8000/rooms/{room_id}
```

**4. Test WebSocket URL Format:**

Correct formats:
```
? ws://localhost:8000/ws/room123/user456
? wss://your-domain.com/ws/abc-def-ghi/xyz-uvw-rst
```

Incorrect formats:
```
? ws://localhost:8000/ws/room123           (missing user_id)
? ws://localhost:8000/ws                   (missing both)
? ws://localhost:8000/websocket/room/user  (wrong path)
```

---

## ?? Quick Fix Script

Run this to test the complete flow:

```bash
python test_websocket_fix.py
```

This script:
1. ? Creates a user
2. ? Creates a room
3. ? Joins the room (HTTP API)
4. ? Connects WebSocket
5. ? Sends a message
6. ? Verifies broadcast

---

## ?? Production Deployment Checklist

Before deploying to Railway:

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `ALLOW_WEBSOCKET_AUTO_ROOMS=true` (or ensure frontend creates rooms first)
- [ ] Set `ALLOW_JOIN_AUTO_USERS=true` (or ensure frontend creates users first)
- [ ] Test with `test_websocket_fix.py`
- [ ] Verify CORS includes your frontend URL
- [ ] Check Railway logs after deployment
- [ ] Test from frontend in browser

---

## ?? Summary

**The Issue:**
Your WebSocket implementation is correct, but it requires users and rooms to exist BEFORE connecting. The frontend is likely trying to connect without creating them first.

**The Fix:**
1. **Best Solution:** Update frontend to create user ? create room ? join room ? connect WebSocket
2. **Quick Solution:** Enable auto-creation in production via environment variables
3. **Dev Solution:** Modify backend to always auto-create

**Choose the solution that fits your security/convenience needs!**

---

## ?? Still Having Issues?

If none of these solutions work, check:
1. **Firewall/Network:** Is WebSocket traffic being blocked?
2. **Proxy/Load Balancer:** Is your proxy configured for WebSocket upgrade?
3. **Railway Config:** Check Railway logs for WebSocket-related errors
4. **Browser Support:** Test in a different browser (Chrome/Firefox)

**Collect this info for debugging:**
- Browser console errors (full text)
- Server logs (from Railway or local)
- Network tab showing WebSocket request
- Environment variables set in Railway
