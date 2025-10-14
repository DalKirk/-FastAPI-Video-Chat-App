# FastAPI Real-Time Chat Application

A modern real-time chat application built with FastAPI and WebSockets, optimized for mobile and desktop use.

## 🚀 Features

- **Real-time messaging** with WebSocket support
- **Multi-room chat** - Create and join different chat rooms
- **User management** - Simple user creation and management
- **Mobile responsive** - Works perfectly on mobile devices
- **Cross-platform** - Supports both HTTP and HTTPS deployments
- **Production ready** - Optimized for Railway deployment

## 🛠️ Technology Stack

- **Backend**: FastAPI with WebSocket support
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Database**: In-memory storage (can be extended to use a database)
- **Deployment**: Railway-optimized with Procfile

## 📱 Live Demo

Visit the live application: [Railway Deployment URL]

## 🔧 Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd FastAPI-Chat
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the chat**
   Open your browser to `http://localhost:8000/chat`

## 🚀 Railway Deployment

This application is pre-configured for Railway deployment with:

- `Procfile` - Railway startup configuration
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `main.py` - Production-ready FastAPI application

Simply connect this repository to Railway for automatic deployment.

## 🎯 How to Use

1. **Create a user** - Enter your username and click "Create User"
2. **Create or join a room** - Either create a new room or join an existing one
3. **Start chatting** - Send real-time messages to other users in the room

## 🔧 API Endpoints

- `GET /` - API status
- `POST /users` - Create a new user
- `GET /users` - Get all users
- `POST /rooms` - Create a new room
- `GET /rooms` - Get all rooms
- `GET /rooms/{room_id}/messages` - Get room messages
- `POST /rooms/{room_id}/join` - Join a room
- `WebSocket /ws/{room_id}/{user_id}` - Real-time chat connection

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to submit a Pull Request.