# ?? FastAPI Video Chat - Complete Deployment Fix

## ? **What Was Fixed**

### 1. **CORS Configuration**
- ? Updated `main.py` to use FastAPI's built-in `CORSMiddleware`
- ? Added support for all Vercel preview deployments
- ? Configured proper credentials and headers
- ? Environment-aware (strict in production, permissive in development)

### 2. **Pydantic v2 Compatibility**
- ? Replaced deprecated `@validator` with `@field_validator`
- ? Updated `class Config` to `model_config = ConfigDict(...)`
- ? All models now compatible with Pydantic 2.0+

### 3. **Dynamic CORS Middleware**
- ? Created `backend/dynamic_cors_middleware.py` for advanced use cases
- ? Currently using FastAPI's built-in middleware (simpler and more reliable)
- ? Can switch to dynamic middleware if needed for more granular control

---

## ?? **Current Configuration**

### **Allowed Origins:**
```python
allowed_origins = [
  "http://localhost:3000",
  "http://localhost:3001",
  "https://localhost:3000",
  "https://next-js-14-front-end-for-chat-plast.vercel.app",
  "https://video-chat-frontend-ruby.vercel.app",
  "https://next-js-14-front-end-for-chat-plaster-repository-7vb273qqo.vercel.app",
]
```

### **Environment Variables Needed:**
```bash
# Required for video features
BUNNY_API_KEY=your_bunny_api_key
BUNNY_LIBRARY_ID=your_library_id
BUNNY_PULL_ZONE=your_pull_zone_domain

# Optional
BUNNY_COLLECTION_ID=your_collection_id
ENVIRONMENT=production  # or development
PORT=8000  # Auto-set by Railway
```

---

## ?? **Deployment Checklist**

### **Before Deploying:**
- [ ] All environment variables set in Railway
- [ ] `requirements.txt` is up to date
- [ ] `Procfile` points to correct main file
- [ ] Frontend URLs are correct in CORS config

### **Deploy to Railway:**
```bash
# Option 1: Git push (if connected to GitHub)
git add .
git commit -m "fix: Update CORS and Pydantic compatibility"
git push origin main

# Option 2: Railway CLI
railway up
```

### **After Deploying:**
- [ ] Check Railway logs for startup messages
- [ ] Test health endpoint: `curl https://your-app.up.railway.app/health`
- [ ] Run verification script: `python test_deployment.py`
- [ ] Test from frontend

---

## ?? **Testing**

### **1. Quick Health Check:**
```bash
curl https://natural-presence-production.up.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "version": "2.0.0",
  "services": {
    "api": "running",
    "websocket": "running",
    "bunny_stream": "enabled"
  }
}
```

### **2. CORS Test:**
```bash
curl -H "Origin: https://next-js-14-front-end-for-chat-plast.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://natural-presence-production.up.railway.app/health
```

**Expected Headers:**
```
Access-Control-Allow-Origin: https://next-js-14-front-end-for-chat-plast.vercel.app
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

### **3. Full Verification:**
```bash
python test_deployment.py
```

---

## ?? **Common Issues & Solutions**

### **Issue: CORS errors in browser**
**Symptom:** `Access to fetch blocked by CORS policy`

**Solution:**
1. Check frontend URL is in `allowed_origins` list
2. Verify backend is deployed with latest code
3. Check browser console for exact origin being sent
4. Add missing origin to list and redeploy

### **Issue: WebSocket connection fails**
**Symptom:** `WebSocket connection to 'wss://...' failed`

**Solution:**
1. Ensure user and room are created before connecting
2. Check URL format: `wss://backend.com/ws/{room_id}/{user_id}`
3. Verify backend logs for connection attempts
4. Test with built-in chat UI: `https://backend.com/chat`

### **Issue: Bunny.net features not working**
**Symptom:** Live stream/upload returns mock data

**Solution:**
1. Check environment variables are set in Railway
2. Test Bunny.net API: `https://backend.com/test-bunny`
3. Verify API key has correct permissions
4. Check Railway logs for Bunny.net API errors

---

## ?? **Monitoring**

### **Railway Dashboard:**
- Monitor CPU/Memory usage
- Check deployment logs
- View request metrics

### **Health Endpoint:**
```bash
# Set up a cron job to ping every 10 minutes (prevents Railway sleep)
*/10 * * * * curl https://natural-presence-production.up.railway.app/health
```

### **External Monitoring:**
Use one of these free services:
- [UptimeRobot](https://uptimerobot.com) - 50 monitors free
- [Cronitor](https://cronitor.io) - 5 monitors free
- [Better Uptime](https://betteruptime.com) - 10 monitors free

---

## ?? **Live URLs**

### **Backend (Railway):**
- API: https://natural-presence-production.up.railway.app
- Health: https://natural-presence-production.up.railway.app/health
- Docs: https://natural-presence-production.up.railway.app/docs
- Chat UI: https://natural-presence-production.up.railway.app/chat

### **Frontend (Vercel):**
- Primary: https://next-js-14-front-end-for-chat-plast.vercel.app
- Alternative: https://video-chat-frontend-ruby.vercel.app
- Preview: https://next-js-14-front-end-for-chat-plaster-repository-7vb273qqo.vercel.app

---

## ?? **Success Criteria**

After deployment, verify:
- ? Backend health check returns 200 OK
- ? Frontend can connect to backend (no CORS errors)
- ? Users can create accounts and rooms
- ? Real-time chat works via WebSocket
- ? Video features work (if Bunny.net configured)
- ? API documentation accessible
- ? No errors in Railway logs

---

## ?? **Need Help?**

1. **Check Logs:**
   ```bash
   railway logs --tail
   ```

2. **Verify Environment:**
   ```bash
   railway variables
   ```

3. **Test Locally:**
   ```bash
   python main.py
   # Visit http://localhost:8000/chat
   ```

---

**Last Updated:** January 2025  
**Status:** ? Ready for deployment  
**Next Steps:** Deploy to Railway and test with frontend
