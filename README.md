# 🚀 FastAPI Video Chat Application

A comprehensive real-time video chat application with live streaming capabilities, built with FastAPI, WebSocket support, and Mux video integration.

## 🌟 **Live Deployment**

### **🎯 Production URLs:**
- **🏠 Backend API:** https://natural-presence-production.up.railway.app
- **💚 Health Check:** https://natural-presence-production.up.railway.app/health
- **📚 API Documentation:** https://natural-presence-production.up.railway.app/docs
- **💬 Chat Interface:** https://natural-presence-production.up.railway.app/chat
- **🖥️ Frontend:** https://next-js-14-front-end-for-chat-plast.vercel.app

## ✨ **Features**

### **💬 Real-time Chat:**
- User registration and management
- Room creation and joining
- Real-time messaging via WebSocket
- Message history and persistence
- Mobile-optimized chat interface

### **🎬 Video Integration:**
- **Live Streaming** - Create and broadcast live streams
- **Video Upload** - Upload and share video content
- **Mux Player** - Professional video playback
- **Real-time Notifications** - Video ready alerts
- **Webhook Support** - Mux event processing

### **🔧 Technical Features:**
- **FastAPI** - Modern Python web framework
- **WebSocket** - Real-time bidirectional communication
- **Mux API** - Professional video infrastructure
- **CORS Support** - Cross-origin resource sharing
- **Health Monitoring** - System status endpoints
- **Docker Ready** - Containerized deployment

## 🛠️ **Technology Stack**

- **Backend**: FastAPI, Python 3.9+
- **WebSocket**: Real-time communication
- **Video**: Mux API integration
- **Deployment**: Railway (Backend) + Vercel (Frontend)
- **Database**: In-memory (Redis/PostgreSQL ready)
- **Container**: Docker with health checks

## � **Quick Start**

### **Option 1: Use Live Deployment**
Just visit: https://next-js-14-front-end-for-chat-plast.vercel.app

### **Option 2: Local Development**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DalKirk/FastAPI-Video-Chat-App.git
   cd FastAPI-Video-Chat-App
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main_optimized.py
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
├── main_optimized.py     # Production FastAPI app with Mux
├── main.py              # Basic FastAPI app (no Mux)
├── requirements.txt     # Python dependencies
├── Procfile            # Railway deployment config
├── Dockerfile          # Container configuration
├── deploy.ps1          # Windows deployment script
├── deploy.sh           # Unix deployment script
├── test_api.py         # API testing utilities
└── docs/
    ├── DEPLOYMENT_STATUS.md      # Current deployment info
    ├── RAILWAY_DEPLOY_FIXED.md   # Deployment guide
    └── ROOM_JOIN_FIX.md         # Troubleshooting
```

## � **API Endpoints**

### **Core Chat API:**
- `GET /` - API information
- `GET /health` - System health check
- `POST /users` - Create user
- `GET /users` - List users
- `POST /rooms` - Create room
- `GET /rooms` - List rooms
- `GET /rooms/{room_id}/messages` - Get room messages
- `POST /rooms/{room_id}/join` - Join room

### **Video API (Mux Integration):**
- `POST /rooms/{room_id}/live-stream` - Create live stream
- `GET /rooms/{room_id}/live-streams` - Get room streams
- `POST /rooms/{room_id}/video-upload` - Upload video
- `GET /rooms/{room_id}/videos` - Get room videos
- `POST /mux-webhook` - Mux event webhook

### **WebSocket:**
- `WS /ws/{room_id}/{user_id}` - Real-time chat connection

## 🎬 **Video Features**

### **Mux Integration:**
- **Token ID:** Configured via environment variables
- **Live Streaming:** Create and manage live streams
- **Video Upload:** Direct upload to Mux
- **Playback:** Mux Player embedded in chat
- **Webhooks:** Real-time video processing notifications

### **Video Workflow:**
1. User creates live stream in room
2. Backend creates Mux live stream
3. Stream key provided for broadcasting
4. Real-time notifications sent to room participants
5. Recorded content available for playback

## 🔧 **Configuration**

### **Environment Variables:**
```bash
# Optional Mux Configuration (for video features)
MUX_TOKEN_ID=your-mux-token-id
MUX_TOKEN_SECRET=your-mux-token-secret
MUX_ENVIRONMENT_ID=your-mux-environment-id

# Frontend URL (for CORS)
FRONTEND_URL=https://your-frontend.vercel.app

# Port (Railway sets automatically)
PORT=8000
```

### **Local Development:**
```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

## � **Testing**

### **API Testing:**
```bash
python test_api.py
```

### **Health Check:**
```bash
curl https://natural-presence-production.up.railway.app/health
```

### **WebSocket Testing:**
Open the chat interface and test real-time messaging.

## 🚀 **Deployment Status**

- ✅ **Railway Backend:** https://natural-presence-production.up.railway.app
- ✅ **Vercel Frontend:** https://next-js-14-front-end-for-chat-plast.vercel.app
- ✅ **Mux Integration:** Configured and working
- ✅ **WebSocket:** Real-time messaging active
- ✅ **CORS:** Configured for cross-origin requests
- ✅ **Health Monitoring:** Available at `/health`

## 📞 **Support**

- **Documentation:** Check the `/docs` folder
- **API Docs:** Visit `/docs` endpoint on the live server
- **Health Status:** Monitor via `/health` endpoint
- **Logs:** Use `railway logs` for deployment debugging

## 🔄 **Development Workflow**

1. **Local Development:** Use `main.py` for basic chat
2. **Video Features:** Use `main_optimized.py` with Mux
3. **Testing:** Run `test_api.py` for API validation
4. **Deployment:** Use `deploy.ps1` or `deploy.sh`
5. **Monitoring:** Check `/health` and Railway dashboard

## 🎯 **Next Steps**

- [ ] Add persistent database (PostgreSQL/MongoDB)
- [ ] Implement user authentication (JWT)
- [ ] Add file sharing capabilities
- [ ] Enhanced video controls and settings
- [ ] Mobile app development (React Native)
- [ ] Advanced moderation features

---

**Built with ❤️ using FastAPI, Mux, Railway, and Vercel**