package com.yourcompany.chatapp.network

import com.yourcompany.chatapp.models.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    
    @GET("/")
    suspend fun getRoot(): Response<Map<String, String>>
    
    @POST("users")
    suspend fun createUser(@Body request: UserCreateRequest): Response<User>
    
    @GET("users")
    suspend fun getUsers(): Response<List<User>>
    
    @POST("rooms")
    suspend fun createRoom(@Body request: RoomCreateRequest): Response<Room>
    
    @GET("rooms")
    suspend fun getRooms(): Response<List<Room>>
    
    @GET("rooms/{roomId}")
    suspend fun getRoom(@Path("roomId") roomId: String): Response<Room>
    
    @GET("rooms/{roomId}/messages")
    suspend fun getRoomMessages(
        @Path("roomId") roomId: String,
        @Query("limit") limit: Int = 50
    ): Response<List<Message>>
    
    @POST("rooms/{roomId}/join")
    suspend fun joinRoom(
        @Path("roomId") roomId: String,
        @Body request: JoinRoomRequest
    ): Response<Map<String, String>>
}