# Android Integration Guide

This guide shows how to integrate your FastAPI Chat API with Android Studio for native Android development.

## Project Structure

```
android_chat_app/
├── app/
│   ├── src/main/java/com/yourcompany/chatapp/
│   │   ├── MainActivity.kt
│   │   ├── ChatActivity.kt
│   │   ├── models/
│   │   │   ├── User.kt
│   │   │   ├── Room.kt
│   │   │   └── Message.kt
│   │   ├── network/
│   │   │   ├── ApiService.kt
│   │   │   ├── WebSocketManager.kt
│   │   │   └── RetrofitClient.kt
│   │   └── adapters/
│   │       ├── RoomAdapter.kt
│   │       └── MessageAdapter.kt
│   ├── src/main/res/
│   │   ├── layout/
│   │   │   ├── activity_main.xml
│   │   │   ├── activity_chat.xml
│   │   │   ├── item_room.xml
│   │   │   └── item_message.xml
│   │   └── values/
│   │       ├── strings.xml
│   │       └── colors.xml
│   └── build.gradle.kts
├── gradle/
└── build.gradle.kts
```

## Setup Instructions

1. Create new Android Studio project
2. Add dependencies to `build.gradle.kts`
3. Add network permissions to `AndroidManifest.xml`
4. Copy the provided source files
5. Update API base URL to your Railway deployment

## API Base URL

Replace `BASE_URL` in `RetrofitClient.kt` with:
- Local development: `http://10.0.2.2:8000/` (Android emulator)
- Production: `https://web-production-64adb.up.railway.app/`

## Features

- ✅ Native Android UI with Material Design
- ✅ Real-time WebSocket messaging
- ✅ Room creation and joining
- ✅ User management
- ✅ Message history
- ✅ Sound notifications
- ✅ Offline message queue
- ✅ Auto-reconnection