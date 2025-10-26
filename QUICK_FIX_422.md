# FIX: Remove Legacy /ai/generate Endpoint

## Problem
Railway's health checks are hitting `/ai/generate` with empty payloads, causing 422 errors in logs.

## Root Cause
Line 28 in `main.py` imports `ai_router` and line 252 includes it, exposing `/ai/generate`.

## Solution
Comment out or remove these lines from `main.py`:

### Line 28 - Remove import:
```python
# BEFORE:
from utils.ai_endpoints import ai_router

# AFTER:
# from utils.ai_endpoints import ai_router  # REMOVED - legacy endpoint
```

### Line 252 - Remove router inclusion:
```python
# BEFORE:
app.include_router(ai_router)
app.include_router(streaming_ai_router)
app.include_router(chat_router)

# AFTER:
# app.include_router(ai_router)  # REMOVED - causing 422 errors
app.include_router(streaming_ai_router)
app.include_router(chat_router)
```

## What This Does
- Removes the `/ai/generate` endpoint entirely
- Keeps `/ai/stream/*` for streaming
- Keeps `/api/v1/chat` for context-aware chat (what your frontend uses)
- Stops the 422 errors in Railway logs

## Your Frontend
No changes needed. It uses `/api/v1/chat` which remains active.

## Next Step
Make these edits in `main.py`, commit, and push to GitHub.
