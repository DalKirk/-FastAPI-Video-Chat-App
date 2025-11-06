# ?? Debugging 405 Error - 3D Model Generation

## Error Details

```
? Generate 3D model failed: AxiosError
Status: 405 Method Not Allowed
Endpoint: /api/v1/3d/generate
```

## Possible Causes & Solutions

### 1. CORS Preflight Failing ??

**Symptom:** Browser sends OPTIONS request, server returns 405

**Fix:**
- ? Moved OPTIONS handler after router registration in `main.py`
- ? Added proper CORS headers

**Test:**
```sh
curl -X OPTIONS https://web-production-3ba7e.up.railway.app/api/v1/3d/generate \
  -H "Origin: https://next-js-14-front-end-for-chat-plast-kappa.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

**Expected:** Status 200 with CORS headers

---

### 2. Wrong HTTP Method ??

**Check Frontend Code:**
```typescript
// WRONG ?
const response = await fetch('/api/v1/3d/generate', {
  method: 'GET'  // Should be POST!
});

// CORRECT ?
const response = await fetch('/api/v1/3d/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'A red cube',
    style: 'realistic',
    complexity: 'simple'
  })
});
```

---

### 3. Rate Limiting ??

**Check if endpoint is excluded:**
```python
# In main.py
per_endpoint_limits = {
    "/api/v1/chat": RateLimitConfig(requests_limit=20, time_window=60),
}
```

**Solution:** 3D endpoint should NOT be in rate limits (it's not, so this is fine)

---

### 4. Router Registration Order ??

**Current Order (Fixed):**
```python
# Middleware first
app.add_middleware(RateLimitMiddleware, ...)
app.add_middleware(CORSMiddleware, ...)

# Then routers
app.include_router(streaming_ai_router)
app.include_router(chat_router)
app.include_router(vision_router)
app.include_router(model_3d_router)  # ? Registered

# OPTIONS handler LAST
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return Response(status_code=200, headers={...})
```

---

### 5. Frontend API Base URL ??

**Check your frontend environment:**
```typescript
// .env.local or .env.production
NEXT_PUBLIC_API_URL=https://web-production-3ba7e.up.railway.app
```

**In your API client:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  generate3DModel: async (prompt: string) => {
    const response = await fetch(`${API_BASE_URL}/api/v1/3d/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, style: 'realistic' })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return response.json();
  }
};
```

---

## Quick Fix Steps

### Step 1: Commit Backend Fix
```sh
cd C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python
git add main.py
git commit -m "fix: move OPTIONS handler after routers to prevent 405 errors"
git push origin main
```

### Step 2: Wait for Railway Deploy (~2 mins)

### Step 3: Test from Command Line
```sh
# Test health endpoint
curl https://web-production-3ba7e.up.railway.app/api/v1/3d/health

# Test generate endpoint
curl -X POST https://web-production-3ba7e.up.railway.app/api/v1/3d/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A red cube", "style": "realistic"}'
```

### Step 4: Check Frontend API Call

**Look for this in your frontend code:**
```typescript
// lib/api.ts or similar
export const generate3DModel = async (prompt: string) => {
  try {
    const response = await api.post('/api/v1/3d/generate', {  // ? Correct path
      prompt,
      style: 'realistic',
      complexity: 'medium'
    });
    return response.data;
  } catch (error) {
    console.error('Generate 3D model failed:', error);
    throw error;
  }
};
```

---

## Debugging Commands

### Check if endpoint exists:
```sh
curl -X GET https://web-production-3ba7e.up.railway.app/docs
# Look for /api/v1/3d/generate in the OpenAPI docs
```

### Check CORS headers:
```sh
curl -I -X OPTIONS https://web-production-3ba7e.up.railway.app/api/v1/3d/generate \
  -H "Origin: https://next-js-14-front-end-for-chat-plast-kappa.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```

**Expected headers:**
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

### Check Railway logs:
```sh
# In Railway dashboard, check application logs for:
# - "POST /api/v1/3d/generate" requests
# - Any error messages
# - CORS-related warnings
```

---

## Frontend Checklist

### ? Verify API Client:

```typescript
// 1. Check base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;
console.log('API Base URL:', API_BASE_URL);
// Should be: https://web-production-3ba7e.up.railway.app

// 2. Check request method
const response = await fetch(`${API_BASE_URL}/api/v1/3d/generate`, {
  method: 'POST',  // ? Must be POST
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    prompt: 'A red cube',
    style: 'realistic',
    complexity: 'simple'
  })
});

// 3. Check response
if (!response.ok) {
  console.error('Status:', response.status);
  console.error('Text:', await response.text());
  throw new Error(`HTTP ${response.status}`);
}
```

---

## Common Frontend Mistakes

### ? Wrong 1: Missing NEXT_PUBLIC_ prefix
```typescript
// .env
API_URL=...  // ? Won't work in browser

// Should be:
NEXT_PUBLIC_API_URL=...  // ? Accessible in browser
```

### ? Wrong 2: Relative path without proxy
```typescript
// If you're calling:
fetch('/api/v1/3d/generate')  // ? Goes to Vercel, not Railway

// Should be:
fetch('https://web-production-3ba7e.up.railway.app/api/v1/3d/generate')  // ?
```

### ? Wrong 3: axios baseURL not set
```typescript
// If using axios:
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL  // ? Set this!
});

api.post('/api/v1/3d/generate', { prompt: '...' });
```

---

## Expected Flow

### 1. Browser sends OPTIONS (preflight):
```http
OPTIONS /api/v1/3d/generate HTTP/1.1
Origin: https://next-js-14-front-end-for-chat-plast-kappa.vercel.app
Access-Control-Request-Method: POST
```

### 2. Server responds with CORS headers:
```http
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

### 3. Browser sends actual POST:
```http
POST /api/v1/3d/generate HTTP/1.1
Content-Type: application/json

{"prompt": "A red cube", "style": "realistic"}
```

### 4. Server processes and returns:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "model_id": "abc123",
  "status": "completed",
  "model_url": "/static/models/abc123.glb"
}
```

---

## If Still Not Working

### Check Railway Environment:
1. Go to Railway dashboard
2. Check if deployment succeeded
3. Look for any startup errors
4. Verify `trimesh` is installed

### Check Frontend Console:
```javascript
// Add this to your API call:
console.log('Request URL:', url);
console.log('Request method:', method);
console.log('Request body:', body);
console.log('Response status:', response.status);
console.log('Response headers:', response.headers);
```

### Test with curl from different origins:
```sh
# From localhost
curl -X POST http://localhost:8000/api/v1/3d/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'

# From Railway
curl -X POST https://web-production-3ba7e.up.railway.app/api/v1/3d/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

---

## Final Checklist

- [ ] Backend: OPTIONS handler is AFTER routers
- [ ] Backend: CORS middleware configured
- [ ] Backend: Router registered in main.py
- [ ] Backend: Endpoint uses `@router.post()`
- [ ] Frontend: Using POST method
- [ ] Frontend: Correct base URL
- [ ] Frontend: Content-Type header set
- [ ] Frontend: Valid JSON body
- [ ] Railway: Deployment succeeded
- [ ] Railway: trimesh installed

---

**After pushing the fix, test in ~2 minutes once Railway redeploys!** ??
