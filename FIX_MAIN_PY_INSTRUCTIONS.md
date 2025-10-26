# MANUAL FIX REQUIRED: Remove Legacy AI Router from main.py

## Problem
The legacy `/ai/generate` endpoint is causing 422 errors. It needs to be removed.

## Solution

### Step 1: Edit main.py Line 28
Find this line:
```python
from utils.ai_endpoints import ai_router
```

Replace with:
```python
# from utils.ai_endpoints import ai_router  # REMOVED - causing 422 errors with /ai/generate
```

### Step 2: Edit main.py Line 252
Find this line:
```python
app.include_router(ai_router)
```

Replace with:
```python
# app.include_router(ai_router)  # REMOVED - causing 422 errors
```

### Keep These Lines (DON'T CHANGE):
```python
app.include_router(streaming_ai_router)  # Keep for /ai/stream/*
app.include_router(chat_router)          # Keep for /api/v1/chat (your frontend uses this)
```

## After Making Changes

1. Save main.py
2. Run: `git add main.py`
3. Run: `git commit -m "Remove legacy ai_router to fix 422 errors"`
4. Run: `git push`

Railway will auto-deploy and the 422 errors will stop.

## What This Does
- Removes `/ai/generate` endpoint (no longer needed)
- Keeps `/ai/stream/*` for streaming
- Keeps `/api/v1/chat` for your React frontend (the one that works!)
- Stops Railway health checks from hitting non-existent endpoints

Your React app will continue to work perfectly because it uses `/api/v1/chat`.
