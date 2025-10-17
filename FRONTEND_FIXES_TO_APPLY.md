# 🔧 Frontend Fixes - Apply These Changes

## 📍 Location: `c:\Users\g-kd\OneDrive\Desktop\video-chat-frontend`

---

## ❌ **Problems Identified:**

1. **WebSocket connecting before backend room join** - causes 4004 close code
2. **Duplicate toast notifications** - "Connected" then "Disconnected" repeatedly  
3. **No error handling for failed room joins**
4. **WebSocket reconnecting even after max attempts**

---

## ✅ **Fixes to Apply:**

### **Fix 1: Update `app/room/[id]/page.tsx` - initializeWebSocket function**

**Find this code (around line 92-135):**
```typescript
const initializeWebSocket = async (userData?: User) => {
  const currentUser = userData || user;
  if (!currentUser) return;

  try {
    console.log('🔌 Attempting WebSocket connection...');
    setConnectionAttempts(prev => prev + 1);

    // Connect to WebSocket
    socketManager.connect(roomId, currentUser.id);
```

**Replace with:**
```typescript
const initializeWebSocket = async (userData?: User) => {
  const currentUser = userData || user;
  if (!currentUser) return;

  try {
    console.log('🔌 Initializing chat connection...');
    
    // STEP 1: Join room on backend FIRST (this is critical!)
    try {
      await apiClient.joinRoom(roomId, currentUser.id);
      console.log('✅ Joined room on backend successfully');
    } catch (joinError) {
      console.error('❌ Failed to join room on backend:', joinError);
      toast.error('Could not join this room. It may not exist or the server is unavailable.');
      setIsConnected(false);
      setWsConnected(false);
      return; // Stop here - don't attempt WebSocket if backend join fails
    }

    // STEP 2: NOW connect WebSocket (only after successful room join)
    setConnectionAttempts(prev => prev + 1);
    socketManager.connect(roomId, currentUser.id);
```

---

### **Fix 2: Update `app/room/[id]/page.tsx` - Connection callback (around line 140-150)**

**Find this code:**
```typescript
// Handle connection status
socketManager.onConnect((connected: boolean) => {
  setWsConnected(connected);
  setIsConnected(connected);

  if (connected) {
    toast.success('Connected to real-time chat!');
    console.log('✅ WebSocket connected - real-time messaging active');
  } else {
    console.log('❌ WebSocket disconnected');
    if (connectionAttempts === 1) {
      toast.error('Could not connect to real-time server. Check if your backend is running.');
    }
  }
});
```

**Replace with:**
```typescript
// Handle connection status
socketManager.onConnect((connected: boolean) => {
  setWsConnected(connected);
  setIsConnected(connected);

  if (connected) {
    // Only show success toast on FIRST connection (not on reconnects)
    if (!isConnected) {
      toast.success('Connected to real-time chat!', { 
        duration: 2000,
        id: 'ws-connected' // Prevents duplicate toasts
      });
    }
    console.log('✅ WebSocket connected - real-time messaging active');
  } else {
    console.log('⚠️ WebSocket disconnected - attempting to reconnect...');
    // Don't show error toast here - reconnection is automatic
    // Only show error if it's a first-time connection failure
  }
});
```

---

### **Fix 3: Update `app/room/[id]/page.tsx` - useEffect cleanup (around line 80-95)**

**Find this code:**
```typescript
useEffect(() => {
  // Get user from localStorage
  const savedUser = localStorage.getItem('chat-user');
  if (savedUser) {
    const userData = JSON.parse(savedUser);
    setUser(userData);

    // Load initial messages
    loadMessages();

    // Initialize WebSocket connection after user is set
    setTimeout(() => {
      initializeWebSocket(userData);
    }, 100);
  } else {
    router.push('/');
    return;
  }

  // Cleanup WebSocket on unmount
  return () => {
    socketManager.disconnect();
  };
}, [roomId, router]);
```

**Replace with:**
```typescript
useEffect(() => {
  // Get user from localStorage
  const savedUser = localStorage.getItem('chat-user');
  if (savedUser) {
    const userData = JSON.parse(savedUser);
    setUser(userData);

    // Load initial messages
    loadMessages();

    // Initialize WebSocket connection after user is set
    setTimeout(() => {
      initializeWebSocket(userData);
    }, 100);
  } else {
    router.push('/');
    return;
  }

  // Cleanup WebSocket on unmount
  return () => {
    console.log('🧹 Cleaning up room - disconnecting WebSocket');
    socketManager.disconnect();
    setWsConnected(false);
    setIsConnected(false);
  };
}, [roomId, router]);
```

---

### **Fix 4: Update `lib/socket.ts` - Improve reconnection logic**

**Find this code (around line 48-60):**
```typescript
this.socket.onclose = (event) => {
  console.log('❌ Disconnected from WebSocket:', event.code, event.reason);
  this.callbacks.get('connect')?.(false);

  // Auto-reconnect with exponential backoff
  if (this.reconnectAttempts < this.maxReconnectAttempts) {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    setTimeout(() => this.connect(roomId, userId), delay);
  } else {
    console.error('❌ Max reconnection attempts reached');
  }
};
```

**Replace with:**
```typescript
this.socket.onclose = (event) => {
  console.log('❌ Disconnected from WebSocket:', event.code, event.reason);
  this.callbacks.get('connect')?.(false);

  // Check close codes
  if (event.code === 4004) {
    // Custom code: User/Room not found - don't reconnect
    console.error('❌ Room or user not found on backend. Cannot reconnect.');
    this.callbacks.get('error')?.(new Error('Room or user not found'));
    return;
  }

  // Auto-reconnect with exponential backoff
  if (this.reconnectAttempts < this.maxReconnectAttempts) {
    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    console.log(`🔄 Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
    setTimeout(() => this.connect(this.roomId, this.userId), delay);
  } else {
    console.error('❌ Max reconnection attempts reached');
    this.callbacks.get('error')?.(new Error('Max reconnection attempts reached'));
  }
};
```

---

### **Fix 5: Add error callback to `lib/socket.ts`**

**Add this method (around line 120):**
```typescript
onError(callback: (error: Error) => void): void {
  this.callbacks.set('error', callback);
}
```

---

## 📝 **How to Apply These Fixes:**

```powershell
# 1. Navigate to frontend directory
cd c:\Users\g-kd\OneDrive\Desktop\video-chat-frontend

# 2. Open the files in VS Code
code app/room/[id]/page.tsx
code lib/socket.ts

# 3. Apply the changes above

# 4. Test locally (optional)
npm run dev
# Visit http://localhost:3000

# 5. Commit and push
git add .
git commit -m "fix: Resolve WebSocket connection issues - join room before WS connect"
git push origin master

# 6. Wait for Vercel deployment (1-2 minutes)
# Visit your live site to test
```

---

## ✅ **Expected Results After Fixes:**

1. **Single toast notification**: "Connected to real-time chat!" (only once)
2. **No repeated connect/disconnect messages**
3. **Proper error handling**: If room doesn't exist, clear error message
4. **Stable connection**: WebSocket stays connected
5. **Clean reconnection**: Automatic reconnect on network issues
6. **Proper cleanup**: WebSocket disconnects when leaving room

---

## 🧪 **Testing Checklist:**

After deploying:

- [ ] Create a user
- [ ] Create a new room
- [ ] **Expected**: ONE "Connected to real-time chat!" toast
- [ ] **Expected**: NO "Disconnected" toast immediately after
- [ ] Send a message
- [ ] **Expected**: Message appears instantly
- [ ] Open in second browser tab
- [ ] **Expected**: Messages sync between tabs in real-time
- [ ] Close tab and reopen
- [ ] **Expected**: Can reconnect without errors
- [ ] Try joining non-existent room (edit URL)
- [ ] **Expected**: Clear error message, no infinite reconnect loop

---

## 📊 **Root Cause Summary:**

**Problem**: WebSocket was trying to connect to `/ws/{room}/{user}` BEFORE the user was added to the room on the backend. The backend checks if the user and room exist, and if not, closes the connection with code 4004.

**Solution**: Always call `apiClient.joinRoom()` FIRST, then connect WebSocket. This ensures the backend knows about the user-room relationship before accepting the WebSocket connection.

---

## 🆘 **If Issues Persist:**

1. **Check backend logs:**
   ```powershell
   railway logs
   ```

2. **Check browser console** for errors

3. **Verify backend health:**
   ```powershell
   curl https://natural-presence-production.up.railway.app/health
   ```

4. **Test WebSocket directly:**
   ```javascript
   // In browser console
   const ws = new WebSocket('wss://natural-presence-production.up.railway.app/ws/test-room/test-user');
   ws.onopen = () => console.log('Connected');
   ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
   ```

---

**Status**: Ready to apply  
**Estimated Time**: 10 minutes  
**Risk Level**: Low (only fixes connection logic)  
**Testing Required**: Yes (test in production after deploy)

