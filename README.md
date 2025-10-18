# 🚀 FastAPI Video Chat Application

A comprehensive real-time video chat application with live streaming capabilities, built with FastAPI, WebSocket support, and **Bunny.net Stream** video integration.

## 🌟 **Live Deployment**

### **🎯 Production URLs:**
- **🏠 Backend API:** https://natural-presence-production.up.railway.app
- **💚 Health Check:** https://natural-presence-production.up.railway.app/health
- **📚 API Documentation:** https://natural-presence-production.up.railway.app/docs
- **💬 Chat Interface:** https://natural-presence-production.up.railway.app/chat
- **🖥️ Frontend (Primary):** https://next-js-14-front-end-for-chat-plast.vercel.app
- **🖥️ Frontend (Alternative):** https://video-chat-frontend-ruby.vercel.app

> **⚠️ Note:** Railway free tier services sleep after inactivity. If you see a 502 error, the backend is waking up (takes 2-3 minutes).

## ✨ **Features**

### **💬 Real-time Chat:**
- User registration and management
- Room creation and joining
- Real-time messaging via WebSocket
- Message history and persistence
- Mobile-optimized chat interface

### **🎬 Video Integration:**
- **Live Streaming** - Create and broadcast live streams via Bunny.net Stream
- **Video Upload** - Upload and share video content to Bunny.net storage
- **HLS Playback** - Professional video playback with HLS.js
- **Real-time Notifications** - Video processing status updates
- **Webhook Support** - Bunny.net event processing

### **🔧 Technical Features:**
- **FastAPI** - Modern Python web framework
- **WebSocket** - Real-time bidirectional communication
- **Bunny.net Stream** - Cost-effective video infrastructure
- **CORS Support** - Cross-origin resource sharing
- **Health Monitoring** - System status endpoints
- **Docker Ready** - Containerized deployment

## 🛠️ **Technology Stack**

- **Backend**: FastAPI, Python 3.14+
- **WebSocket**: Real-time communication
- **Video**: Bunny.net Stream API (replacing Mux)
- **Deployment**: Railway (Backend) + Vercel (Frontend)
- **Database**: In-memory (Redis/PostgreSQL ready)
- **Container**: Docker with health checks
- **Video Player**: HLS.js for cross-browser compatibility

## 📊 **Cost Comparison**

| Feature | Mux (Previous) | Bunny.net Stream (Current) | Savings |
|---------|----------------|---------------------------|---------|
| Video Storage | $0.50/GB/month | $0.01/GB/month | **98% cheaper** |
| Video Delivery | $0.10/GB | $0.005/GB | **95% cheaper** |
| Live Streaming | $0.10/minute | $0.005/minute | **95% cheaper** |
| Free Tier | Limited | 10GB storage + 100GB bandwidth | **Much more generous** |

## 🚀 **Quick Start**

### **Option 1: Use Live Deployment**
Just visit: https://next-js-14-front-end-for-chat-plast.vercel.app

### **Option 2: Local Development**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DalKirk/-FastAPI-Video-Chat-App.git
   cd -FastAPI-Video-Chat-App
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Open your browser:**
   ```
   http://localhost:8000/chat
   ```

## 🌐 **Deployment**

### **Railway Deployment (Automated):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy with our script
./deploy.ps1  # Windows
./deploy.sh   # Linux/Mac
```

### **Manual Deployment:**
```bash
railway login
railway init
railway up
```

## 📁 **Project Structure**

```
├── main.py              # Production FastAPI app with Bunny.net Stream
├── main_backup.py       # Backup version
├── requirements.txt     # Python dependencies (Python 3.14 compatible)
├── Procfile            # Railway deployment config
├── Dockerfile          # Container configuration
├── deploy.ps1          # Windows deployment script
├── deploy.sh           # Unix deployment script
├── test_api.py         # API testing utilities
├── test_websocket.py   # WebSocket testing
├── test_timestamps.py  # Timestamp validation
└── docs/
    ├── DEPLOYMENT_STATUS.md      # Current deployment info
    ├── RAILWAY_DEPLOY_FIXED.md   # Deployment guide
    ├── WEBSOCKET_FIX.md         # WebSocket troubleshooting
    └── ROOM_JOIN_FIX.md         # Room joining fixes
```

## 🔗 **API Endpoints**

### **Core Chat API:**
- `GET /` - API information
- `GET /health` - System health check
- `GET /test-bunny` - Bunny.net API connectivity test
- `POST /users` - Create user
- `GET /users` - List users
- `POST /rooms` - Create room
- `GET /rooms` - List rooms
- `GET /rooms/{room_id}/messages` - Get room messages
- `POST /rooms/{room_id}/join` - Join room

### **Video API (Bunny.net Stream Integration):**
- `POST /rooms/{room_id}/live-stream` - Create live stream
- `GET /rooms/{room_id}/live-streams` - Get room streams
- `POST /rooms/{room_id}/video-upload` - Upload video
- `GET /rooms/{room_id}/videos` - Get room videos
- `POST /bunny-webhook` - Bunny.net event webhook

### **WebSocket:**
- `WS /ws/{room_id}/{user_id}` - Real-time chat connection

## 🎬 **Video Features**

### **Bunny.net Stream Integration:**
- **API Key:** Configured via environment variables
- **Live Streaming:** Create and manage live streams
- **Video Upload:** Direct upload to Bunny.net storage
- **Playback:** HLS streams via Bunny.net CDN
- **Webhooks:** Real-time video processing notifications

### **Video Workflow:**
1. User creates live stream in room
2. Backend creates Bunny.net live stream
3. Stream key provided for broadcasting (use in OBS/Streamlabs)
4. Real-time notifications sent to room participants
5. Recorded content available for HLS playback

### **Supported Formats:**
- **Upload:** MP4, MOV, AVI, MKV, WebM
- **Live Streaming:** RTMP input, HLS output
- **Playback:** HLS.js player (works on all modern browsers)

## 🔧 **Configuration**

### **Environment Variables:**
```bash
# Required Bunny.net Configuration
BUNNY_API_KEY=your-bunny-api-key
BUNNY_LIBRARY_ID=your-library-id
BUNNY_PULL_ZONE=your-pull-zone-domain

# Optional Configuration
BUNNY_COLLECTION_ID=your-collection-id  # Optional grouping

# Frontend URL (for CORS)
FRONTEND_URL=https://your-frontend.vercel.app

# Port (Railway sets automatically)
PORT=8000
```

### **Getting Bunny.net Credentials:**

1. **Sign up:** https://panel.bunny.net/
2. **Create Video Library:** Go to Stream → Video Library → Add Library
3. **Get Library ID:** From the library settings
4. **Get Pull Zone:** Create a Pull Zone for your library
5. **API Key:** Account → API Key

### **Local Development:**
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

## 🧪 **Testing**

### **API Testing:**
```bash
python test_api.py
```

### **WebSocket Testing:**
```bash
python test_websocket.py
```

### **Health Check:**
```bash
curl https://natural-presence-production.up.railway.app/health
# Should return: {"bunny_stream": "enabled"}
```

### **Bunny.net API Test:**
```bash
curl https://natural-presence-production.up.railway.app/test-bunny
# Should return: {"status": "success"}
```

### **Full Integration Test:**
1. Visit the chat interface
2. Create a user and room
3. Try video upload and live streaming
4. Check real-time notifications

## 🚀 **Deployment Status**

- ✅ **Railway Backend:** https://natural-presence-production.up.railway.app
- ✅ **Vercel Frontend:** https://next-js-14-front-end-for-chat-plast.vercel.app
- ✅ **Bunny.net Stream:** Configured and working
- ✅ **WebSocket:** Real-time messaging active
- ✅ **CORS:** Configured for cross-origin requests
- ✅ **Health Monitoring:** Available at `/health`
- ✅ **Python 3.14:** Compatible versions deployed

## 📞 **Support**

- **Documentation:** Check the `/docs` folder
- **API Docs:** Visit `/docs` endpoint on the live server
- **Health Status:** Monitor via `/health` endpoint
- **Bunny.net Status:** Test via `/test-bunny` endpoint
- **Logs:** Use `railway logs` for deployment debugging

## 🔄 **Development Workflow**

1. **Local Development:** Use `main.py` with Bunny.net integration
2. **Video Features:** Bunny.net Stream handles all video processing
3. **Testing:** Run test files for API and WebSocket validation
4. **Deployment:** Use `deploy.ps1` or `deploy.sh`
5. **Monitoring:** Check `/health` and Railway dashboard

## 🎯 **Migration from Mux**

This project was previously using Mux for video services but has been migrated to Bunny.net Stream for:

- **💰 90%+ cost reduction**
- **📈 Better free tier** (10GB storage + 100GB bandwidth)
- **🔧 Simpler API** and easier integration
- **🌍 Global CDN** with excellent performance
- **📱 Better mobile support**

The migration maintains full backward compatibility with existing frontend code.

## 🎯 **Next Steps**

- [ ] Add persistent database (PostgreSQL/MongoDB)
- [ ] Implement user authentication (JWT)
- [ ] Add file sharing capabilities
- [ ] Enhanced video controls and settings
- [ ] Mobile app development (React Native)
- [ ] Advanced moderation features
- [ ] Video analytics and insights

---

**Built with ❤️ using FastAPI, Bunny.net Stream, Railway, and Vercel**

## 🔌 Vercel / ngrok — quick wiring for frontend testing

If your frontend is deployed on Vercel and you want it to talk to a locally running backend for preview testing, do one of the following:

1) Quick temporary tunnel with ngrok (recommended for fast preview)

```powershell
# Start your backend locally first (in the repo root)
& '.\.venv\Scripts\uvicorn.exe' main_optimized:app --host 127.0.0.1 --port 8000

# In another terminal, start ngrok (install from https://ngrok.com if missing)
ngrok http 8000

# ngrok will print a public HTTPS URL like https://a1b2c3d4.ngrok.io
# Copy that URL and set it in your Vercel project (Environment Variables)
# Variable name: NEXT_PUBLIC_API_URL
# Value: https://a1b2c3d4.ngrok.io
```

2) Deploy backend to Railway and set NEXT_PUBLIC_API_URL to the Railway URL in Vercel (recommended for persistent testing)

 - On Railway, set up environment variables: `BUNNY_API_KEY`, `BUNNY_LIBRARY_ID`, `BUNNY_PULL_ZONE`, and `ENVIRONMENT=production`.
 - In Vercel, set `NEXT_PUBLIC_API_URL` to `https://<your-railway-app>.up.railway.app` and redeploy.

Notes:
 - Do not commit secrets (BUNNY_* or other API keys) to the repository. Use Vercel and Railway environment variable pages to store secrets.
 - If using ngrok, remember the tunnel is temporary and will change on restart unless you have a reserved domain (paid ngrok plan).
