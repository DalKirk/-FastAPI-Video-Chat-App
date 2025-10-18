# 🔧 Complete Project Fix & Deployment Guide

## 🚨 **Issue Summary:**

### **Primary Issue:**
- **Backend (Railway):** Not responding (502 Bad Gateway) - Likely sleeping due to inactivity
- **Frontend URLs:** Two different Vercel deployments causing confusion
  - https://next-js-14-front-end-for-chat-plast.vercel.app (configured in code)
  - https://video-chat-frontend-ruby.vercel.app (mentioned but not configured)

## ✅ **Complete Fix Solution:**

### **Step 1: Fix Railway Backend**

The Railway backend needs to be redeployed and kept active.

```bash
cd "c:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

# Redeploy to Railway
railway up

# Wait 2-3 minutes for startup

# Test backend
curl https://natural-presence-production.up.railway.app/health
```

**Alternative:** Run backend locally while fixing:
```bash
python main.py
# Runs on http://localhost:8000
```

### **Step 2: Update Frontend Configuration**

Update the frontend to handle both backend scenarios:

**File: `video-chat-frontend/lib/api.ts`**
```typescript
// Updated API configuration with fallback
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (process.env.NODE_ENV === 'production' 
    ? 'https://natural-presence-production.up.railway.app'
    : 'http://localhost:8000');
```

**File: `video-chat-frontend/.env.local`**
```bash
# Production Railway Backend
NEXT_PUBLIC_API_URL=https://natural-presence-production.up.railway.app
NEXT_PUBLIC_WS_URL=wss://natural-presence-production.up.railway.app
```

### **Step 3: Deploy Frontend Updates**

```bash
cd "c:\Users\g-kd\OneDrive\Desktop\video-chat-frontend"

# Commit changes
git add .
git commit -m "Fix: Update backend URL and improve error handling"
git push

# Vercel will automatically redeploy (1-2 minutes)
```

### **Step 4: Update CORS on Backend**

The backend needs to allow both Vercel URLs:

**File: `main.py`** (already configured):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://localhost:3000",
        "https://next-js-14-front-end-for-chat-plast.vercel.app",
        "https://video-chat-frontend-ruby.vercel.app",  # Add this
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
```

## 🔍 **Verification Steps:**

### **1. Test Backend:**
```bash
# Health check
curl https://natural-presence-production.up.railway.app/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-16T...",
  "services": {
    "api": "running",
    "websocket": "running",
    "bunny_stream": "available"
  }
}
```

### **2. Test Frontend:**
1. Visit: https://next-js-14-front-end-for-chat-plast.vercel.app
2. Open Browser Console (F12)
3. Look for connection messages:
   - "🔧 API Configuration"
   - "🚀 Creating user..."
4. Try creating a username

### **3. Test Complete Flow:**
1. Open frontend
2. Enter username → Click "Get Started"
3. Create a room → Join room
4. Send a message
5. Check real-time updates work

## 🐛 **Common Issues & Fixes:**

### **Issue 1: "Not Connected to Server"**

**Cause:** Backend is sleeping or not responding

**Fix:**
```bash
# Option A: Redeploy Railway
railway up

# Option B: Run locally
python main.py
# Update frontend .env.local to http://localhost:8000
```

### **Issue 2: CORS Errors**

**Cause:** Frontend URL not in backend's allowed origins

**Fix:** Update `main.py` CORS configuration (see Step 4 above)

### **Issue 3: WebSocket Connection Failed**

**Cause:** Wrong WebSocket URL or backend not running

**Fix:**
1. Check backend is running: `curl <backend-url>/health`
2. Verify `NEXT_PUBLIC_WS_URL` in `.env.local`
3. Use `wss://` for HTTPS sites, `ws://` for HTTP

### **Issue 4: Frontend Shows Old Version**

**Cause:** Browser/Vercel CDN caching

**Fix:**
1. Hard refresh: `Ctrl + Shift + R` (or `Cmd + Shift + R` on Mac)
2. Check Vercel dashboard for latest deployment
3. Clear browser cache

## 📊 **Current Configuration:**

### **Backend (Railway):**
- **URL:** https://natural-presence-production.up.railway.app
- **Deployment:** Dockerized FastAPI app
- **Features:** Real-time chat, WebSocket, Bunny.net Stream video integration
- **Status:** Redeploying (2-3 minutes startup time)

### **Frontend (Vercel):**
- **Primary URL:** https://next-js-14-front-end-for-chat-plast.vercel.app
- **Repository:** Next.js-14-Front-End-For-Chat-Plaster-Repository-
- **Configuration:** Points to Railway backend
- **Status:** Active, needs backend connection

## 🚀 **Quick Start (Local Development):**

### **Terminal 1 - Backend:**
```bash
cd "c:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"
python main.py
# Backend runs on http://localhost:8000
```

### **Terminal 2 - Frontend:**
```bash
cd "c:\Users\g-kd\OneDrive\Desktop\video-chat-frontend"

# Update .env.local for local backend:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local

npm run dev
# Frontend runs on http://localhost:3000
```

### **Test:**
1. Open: http://localhost:3000
2. Create username
3. Create room
4. Send messages

## 📝 **Railway Free Tier Limitations:**

**Important:** Railway free tier services:
- ⏰ **Sleep after 15 minutes** of inactivity
- ⏱️ **Cold start time:** 2-3 minutes to wake up
- 🔄 **Solution:** Use a cron job or monitoring service to ping `/health` every 10 minutes

**Keep Railway Alive:**
```bash
# Option 1: Manual ping
curl https://natural-presence-production.up.railway.app/health

# Option 2: Use a free monitoring service
# - UptimeRobot (https://uptimerobot.com)
# - Cronitor (https://cronitor.io)
# - Set to ping every 10 minutes
```

## 🎯 **Action Plan:**

1. **✅ Backend:** Redeployed to Railway
2. **⏳ Waiting:** 2-3 minutes for Railway startup
3. **✅ Frontend:** Code configured correctly
4. **⏳ Test:** Once backend is up, test end-to-end
5. **✅ Documentation:** Updated with troubleshooting

## 📞 **Support Commands:**

```bash
# Check Railway status
railway status

# Redeploy Railway
railway up

# Check Railway logs
railway logs

# Check git status
git status

# Push updates to GitHub
git add .
git commit -m "Update: Fix deployment issues"
git push
```

---

## ⏰ **Expected Timeline:**

- **Right Now:** Backend is starting up on Railway
- **In 2-3 minutes:** Backend should be fully responsive
- **Test Then:** Visit frontend and try creating a user
- **Result:** Should work end-to-end

**Monitor Backend Status:**
```bash
# Run this command every 30 seconds until you get a 200 response
curl -w "\nHTTP Status: %{http_code}\n" https://natural-presence-production.up.railway.app/health
```

When you see "HTTP Status: 200", the backend is ready! 🎉