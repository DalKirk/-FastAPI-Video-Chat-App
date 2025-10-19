# ?? API Documentation

## Overview

FastAPI Video Chat API provides real-time messaging with WebSocket support and video streaming capabilities through Bunny.net Stream integration.

**Base URL (Production):** `https://web-production-3ba7e.up.railway.app`

**API Version:** 2.0.0

---

## Authentication

Currently, the API does not require authentication. Future versions will implement JWT-based authentication.

---

## Core Endpoints

### Health & Status

#### `GET /health`

Health check endpoint for monitoring service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T12:00:00Z",
  "version": "2.0.0",
  "environment": "production",
  "services": {
    "api": "running",
    "websocket": "running",
    "bunny_stream": "enabled"
  },
  "stats": {
    "active_rooms": 5,
    "active_users": 12,
    "total_messages": 348
  }
}
```

#### `GET /`

Root endpoint providing API information.

**Response:**
```json
{
  "message": "FastAPI Video Chat API is running!",
  "version": "2.0.0",
  "docs": "/docs",
  "health": "/health",
  "chat": "/chat",
  "bunny_stream": "enabled"
}
```

---

## User Management

### Create User

**Endpoint:** `POST /users`

Create a new user account.

**Request Body:**
```json
{
  "username": "john_doe"
}
```

**Validation:**
- Username must be 2-50 characters
- Only alphanumeric, hyphens, and underscores allowed

**Response (200):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "joined_at": "2024-01-15T12:00:00Z"
}
```

### Get All Users

**Endpoint:** `GET /users`

Retrieve list of all users.

**Response (200):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "joined_at": "2024-01-15T12:00:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "username": "jane_smith",
    "joined_at": "2024-01-15T13:00:00Z"
  }
]
```

---

## Room Management

### Create Room

**Endpoint:** `POST /rooms`

Create a new chat room.

**Request Body:**
```json
{
  "name": "General Chat"
}
```

**Validation:**
- Room name must be 2-100 characters

**Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "name": "General Chat",
  "created_at": "2024-01-15T12:00:00Z",
  "users": []
}
```

### Get All Rooms

**Endpoint:** `GET /rooms`

Retrieve list of all chat rooms.

**Response (200):**
```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "General Chat",
    "created_at": "2024-01-15T12:00:00Z",
    "users": ["550e8400-e29b-41d4-a716-446655440000"]
  }
]
```

### Get Room by ID

**Endpoint:** `GET /rooms/{room_id}`

Retrieve specific room details.

**Response (200):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "name": "General Chat",
  "created_at": "2024-01-15T12:00:00Z",
  "users": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

**Response (404):**
```json
{
  "detail": "Room not found"
}
```

### Join Room

**Endpoint:** `POST /rooms/{room_id}/join`

Join a chat room.

**Request Body:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response (200):**
```json
{
  "message": "User john_doe joined room General Chat"
}
```

---

## Messages

### Get Room Messages

**Endpoint:** `GET /rooms/{room_id}/messages`

Retrieve message history for a room.

**Query Parameters:**
- `limit` (optional): Maximum number of messages to return (default: 50, max: 100)

**Response (200):**
```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "room_id": "770e8400-e29b-41d4-a716-446655440002",
    "content": "Hello, everyone!",
    "timestamp": "2024-01-15T12:05:00Z"
  }
]
```

---

## WebSocket Communication

### Connect to Room

**Endpoint:** `WS /ws/{room_id}/{user_id}`

Establish WebSocket connection for real-time messaging.

**Message Format (Client ? Server):**
```json
{
  "content": "Hello, World!"
}
```

**Message Format (Server ? Client):**

**Chat Message:**
```json
{
  "type": "message",
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_doe",
  "content": "Hello, World!",
  "timestamp": "2024-01-15T12:05:00Z"
}
```

**User Joined:**
```json
{
  "type": "user_joined",
  "message": "john_doe joined the chat",
  "timestamp": "2024-01-15T12:00:00Z"
}
```

**User Left:**
```json
{
  "type": "user_left",
  "message": "john_doe left the chat",
  "timestamp": "2024-01-15T12:30:00Z"
}
```

---

## Video Streaming

### Create Live Stream

**Endpoint:** `POST /rooms/{room_id}/live-stream`

Create a new live stream for a room.

**Request Body:**
```json
{
  "title": "Gaming Session"
}
```

**Response (200):**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "stream_key": "sk_abc123def456",
  "playback_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "status": "ready",
  "title": "Gaming Session",
  "rtmp_url": "rtmp://rtmp.bunnycdn.com/live/sk_abc123def456",
  "pull_url": "https://pullzone.b-cdn.net/aa0e8400/playlist.m3u8"
}
```

**Usage:**
1. Use `rtmp_url` + `stream_key` in OBS/streaming software
2. Share `pull_url` with viewers for HLS playback

### Get Room Live Streams

**Endpoint:** `GET /rooms/{room_id}/live-streams`

Retrieve all live streams for a room.

**Response (200):**
```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "stream_key": "sk_abc123def456",
    "playback_id": "aa0e8400-e29b-41d4-a716-446655440005",
    "status": "ready",
    "room_id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "Gaming Session",
    "created_at": "2024-01-15T12:00:00Z"
  }
]
```

### Create Video Upload

**Endpoint:** `POST /rooms/{room_id}/video-upload`

Create a video upload session.

**Request Body:**
```json
{
  "title": "My Video",
  "description": "Optional description"
}
```

**Response (200):**
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440006",
  "upload_url": "https://api.example.com/upload-proxy/bb0e8400",
  "status": "pending",
  "title": "My Video"
}
```

### Upload Video File

**Endpoint:** `PUT /upload-proxy/{upload_id}`

Upload video file to the created upload session.

**Request:**
- Content-Type: `video/mp4` (or appropriate video MIME type)
- Body: Binary video file data

**Response (200):**
```json
{
  "status": "uploaded",
  "upload_id": "bb0e8400-e29b-41d4-a716-446655440006"
}
```

### Get Room Videos

**Endpoint:** `GET /rooms/{room_id}/videos`

Retrieve all uploaded videos for a room.

**Response (200):**
```json
[
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "title": "My Video",
    "description": "Optional description",
    "room_id": "770e8400-e29b-41d4-a716-446655440002",
    "status": "ready",
    "created_at": "2024-01-15T12:00:00Z"
  }
]
```

---

## Webhooks

### Bunny.net Webhook

**Endpoint:** `POST /bunny-webhook`

Receive webhooks from Bunny.net for video processing events.

**Event Types:**
- `VideoFileCreated` - Video upload completed
- `VideoFileEncoded` - Video encoding completed

**Request Body Example:**
```json
{
  "EventType": "VideoFileEncoded",
  "VideoGuid": "bb0e8400-e29b-41d4-a716-446655440006"
}
```

**Response (200):**
```json
{
  "status": "received"
}
```

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Status Codes

- `200` - Success
- `400` - Bad Request (validation error)
- `404` - Not Found
- `422` - Unprocessable Entity (Pydantic validation)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting

**Default Limits:**
- 100 requests per 60 seconds per IP
- WebSocket connections: 10 concurrent per IP

**Headers:**
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `Retry-After` - Seconds to wait before retrying

---

## Best Practices

### 1. WebSocket Reconnection
```javascript
function connectWebSocket() {
  const ws = new WebSocket('wss://api.example.com/ws/room_id/user_id');
  
  ws.onclose = () => {
    // Reconnect after 5 seconds
    setTimeout(connectWebSocket, 5000);
  };
}
```

### 2. Message Pagination
```javascript
// Load older messages
const messages = await fetch('/rooms/room_id/messages?limit=50');
```

### 3. Error Handling
```javascript
try {
  const response = await fetch('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'john_doe' })
  });
  
  if (!response.ok) {
    const error = await response.json();
    console.error(error.detail);
  }
} catch (error) {
  console.error('Network error:', error);
}
```

---

## SDKs and Libraries

### JavaScript/TypeScript Example
```typescript
import { io } from 'socket.io-client';

const API_URL = 'https://natural-presence-production.up.railway.app';

// Create user
const createUser = async (username: string) => {
  const response = await fetch(`${API_URL}/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username })
  });
  return response.json();
};

// Connect WebSocket
const connectChat = (roomId: string, userId: string) => {
  const ws = new WebSocket(`wss://${API_URL}/ws/${roomId}/${userId}`);
  
  ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log('Received:', message);
  };
  
  return ws;
};
```

---

## Support

For issues or questions:
- Check the [Interactive API Docs](/docs)
- Review the [GitHub Repository](https://github.com/DalKirk/-FastAPI-Video-Chat-App)
- Monitor service status at `/health`
