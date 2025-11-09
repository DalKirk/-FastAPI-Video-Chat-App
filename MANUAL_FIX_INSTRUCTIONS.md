# MANUAL FIX INSTRUCTIONS

## The terminal commands keep timing out, so here's how to fix it manually:

### Step 1: Download the working main.py from GitHub

Go to: https://github.com/DalKirk/-FastAPI-Video-Chat-App/blob/04309d3/main.py

Click "Raw" button and copy all the content.

### Step 2: Replace your local main.py

1. Open `main.py` in your IDE
2. Select All (Ctrl+A)
3. Paste the content from GitHub
4. Save (Ctrl+S)

### Step 3: Verify the file has endpoints

Search for these strings in the file:
- `def root():`
- `def health_check():`
- `def create_user(`
- `def create_room(`

If you find all of them, the file is good!

### Step 4: Commit and push

```cmd
cd C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python
git add main.py
git commit -m "fix: restore main.py with all endpoints"
git push origin main
```

### Alternative: Use GitHub Desktop

If you have GitHub Desktop:
1. Open the repository
2. Right-click `main.py` ? "Discard Changes"
3. This will restore from the last commit
4. Then commit and push

---

## Quick Verification Checklist

After restoring, your `main.py` should have these sections:

- [ ] Imports (lines 1-30)
- [ ] Data Models (User, Message, Room)
- [ ] ConnectionManager class
- [ ] FastAPI app initialization
- [ ] CORS middleware
- [ ] Rate limiting middleware
- [ ] Router includes (streaming_ai_router, chat_router, vision_router, model_3d_router)
- [ ] Static files mount
- [ ] OPTIONS handler
- [ ] Exception handler
- [ ] **`@app.get("/")`** - Root endpoint
- [ ] **`@app.get("/health")`** - Health check
- [ ] **`@app.post("/users")`** - Create user
- [ ] **`@app.get("/users")`** - List users
- [ ] **`@app.post("/rooms")`** - Create room
- [ ] **`@app.get("/rooms")`** - List rooms
- [ ] **`@app.get("/rooms/{room_id}")`** - Get room
- [ ] **`@app.post("/rooms/{room_id}/join")`** - Join room
- [ ] **`@app.get("/rooms/{room_id}/messages")`** - Get messages
- [ ] Live stream endpoints
- [ ] WebSocket endpoint
- [ ] HTML endpoints

If ANY of the bolded items are missing, the file is still corrupted.

---

## Once Fixed

Railway will auto-deploy and:
- ? Tests will pass
- ? Frontend will work
- ? 3D generation will work
- ? All 405 errors gone

**Follow these manual steps since the terminal is unreliable right now.**
