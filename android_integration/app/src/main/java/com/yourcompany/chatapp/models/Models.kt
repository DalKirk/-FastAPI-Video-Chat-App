package com.yourcompany.chatapp.models

import android.os.Parcelable
import kotlinx.parcelize.Parcelize

@Parcelize
data class User(
    val id: String,
    val username: String,
    val joined_at: String
) : Parcelable

@Parcelize
data class Room(
    val id: String,
    val name: String,
    val created_at: String,
    val users: List<String> = emptyList()
) : Parcelable

@Parcelize
data class Message(
    val id: String,
    val user_id: String,
    val username: String,
    val room_id: String,
    val content: String,
    val timestamp: String
) : Parcelable

// Request models
data class UserCreateRequest(
    val username: String
)

data class RoomCreateRequest(
    val name: String
)

data class JoinRoomRequest(
    val user_id: String
)

// WebSocket message models
data class WebSocketMessage(
    val content: String
)

data class WebSocketResponse(
    val type: String,
    val message: String? = null,
    val id: String? = null,
    val user_id: String? = null,
    val username: String? = null,
    val content: String? = null,
    val timestamp: String? = null
)