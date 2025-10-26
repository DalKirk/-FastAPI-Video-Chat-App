# AI Chat Troubleshooting Guide

## Current Status
- ? Backend deployed with latest commit (3beccad)
- ? Legacy `/ai/generate` endpoint removed
- ? `/api/v1/chat` endpoint active
- ? `ANTHROPIC_API_KEY` set in Railway

## Issue: "AI Offline" Message

### Possible Causes

1. **Railway hasn't redeployed yet**
   - Wait 2-3 minutes after setting `ANTHROPIC_API_KEY`
   - Check Railway logs for "Claude AI client initialized"

2. **Wrong API URL in frontend**
   - Check `REACT_APP_API_URL` environment variable in Vercel
   - Should be: `https://fastapi-video-chat-app-production.up.railway.app`

3. **CORS issue**
   - Verify your Vercel domain is in `allowed_origins` in `main.py`
   - Current allowed origins:
     - `https://next-js-14-front-end-for-chat-plast.vercel.app`
     - `https://next-js-14-front-end-for-chat-plast-kappa.vercel.app`
     - `https://video-chat-frontend-ruby.vercel.app`

## Quick Diagnostics

### 1. Test Backend Health (from terminal)
```sh
curl https://fastapi-video-chat-app-production.up.railway.app/api/v1/chat/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "claude_enabled": true,
  "services": {
    "context_analyzer": "ready",
    "format_selector": "ready",
    "response_formatter": "ready"
  }
}
```

If `claude_enabled: false`, the API key isn't loaded yet.

### 2. Test Chat Endpoint
```sh
curl -X POST https://fastapi-video-chat-app-production.up.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","conversation_history":[]}'
```

**Expected Response:**
```json
{
  "content": "Hello! How can I help you today?",
  "format_type": "conversational",
  "metadata": {...},
  "success": true
}
```

### 3. Check Browser Console
Open DevTools (F12) ? Console tab when on your chat page.

Look for:
- ? **CORS errors**: "Access to fetch at ... has been blocked"
  - Fix: Add your Vercel URL to `allowed_origins` in `main.py`
  
- ? **404 errors**: "Failed to load resource: the server responded with a status of 404"
  - Fix: Check `REACT_APP_API_URL` in Vercel environment variables

- ? **Network errors**: "Failed to fetch"
  - Fix: Verify Railway backend is running

### 4. Check Railway Logs
Go to Railway ? Your Project ? Deployments ? Latest ? Logs

Look for:
```
? Claude AI client initialized with model: claude-sonnet-4-5-20250929
```

If you see:
```
Claude API key not found - AI features disabled
```
Then the API key didn't load. Redeploy manually.

## Solutions

### Solution 1: Redeploy Railway
1. Go to Railway dashboard
2. Click **Deployments**
3. Click **Redeploy** on latest deployment
4. Wait 2-3 minutes

### Solution 2: Add Vercel URL to CORS
If your Vercel URL is not in the list, edit `main.py`:

```python
allowed_origins = [
  "http://localhost:3000",
  # ... existing URLs ...
  "https://your-vercel-app.vercel.app",  # ADD YOUR URL HERE
]
```

Then commit and push:
```sh
git add main.py
git commit -m "Add new Vercel URL to CORS"
git push
```

### Solution 3: Set Frontend API URL
In Vercel:
1. Go to your project settings
2. Environment Variables
3. Add/Update:
   ```
   REACT_APP_API_URL=https://fastapi-video-chat-app-production.up.railway.app
   ```
4. Redeploy frontend

## Verification Steps

After making changes:

1. **Check health endpoint** (should return `claude_enabled: true`)
2. **Test chat in browser** (should get AI response)
3. **Check browser console** (should have no errors)
4. **Check Railway logs** (should show "Claude AI client initialized")

## Still Not Working?

If AI is still offline after all checks:

1. Share your **Vercel URL**
2. Share **Railway logs** (last 50 lines)
3. Share **browser console errors** (screenshot)

## Quick Test Script

Save this as `test-api.sh` and run it:

```bash
#!/bin/bash
API_URL="https://fastapi-video-chat-app-production.up.railway.app"

echo "=== Testing Health ==="
curl -s "$API_URL/api/v1/chat/health" | python -m json.tool

echo -e "\n=== Testing Chat ==="
curl -s -X POST "$API_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Test","conversation_history":[]}' | python -m json.tool
```

Run: `chmod +x test-api.sh && ./test-api.sh`
