package com.yourcompany.chatapp.network

import android.util.Log
import com.google.gson.Gson
import com.yourcompany.chatapp.models.WebSocketMessage
import com.yourcompany.chatapp.models.WebSocketResponse
import org.java_websocket.client.WebSocketClient
import org.java_websocket.handshake.ServerHandshake
import java.net.URI
import java.util.concurrent.ConcurrentLinkedQueue

class WebSocketManager(
    private val roomId: String,
    private val userId: String,
    private val onMessageReceived: (WebSocketResponse) -> Unit,
    private val onConnectionChanged: (Boolean) -> Unit
) {
    private var webSocketClient: WebSocketClient? = null
    private val gson = Gson()
    private val messageQueue = ConcurrentLinkedQueue<String>()
    private var isConnected = false
    
    companion object {
        private const val TAG = "WebSocketManager"
    }
    
    fun connect() {
        try {
            val url = RetrofitClient.getWebSocketUrl(roomId, userId)
            Log.d(TAG, "Connecting to: $url")
            
            val uri = URI(url)
            webSocketClient = object : WebSocketClient(uri) {
                override fun onOpen(handshake: ServerHandshake?) {
                    Log.d(TAG, "WebSocket Connected")
                    isConnected = true
                    onConnectionChanged(true)
                    
                    // Send queued messages
                    while (messageQueue.isNotEmpty()) {
                        val message = messageQueue.poll()
                        message?.let { send(it) }
                    }
                }
                
                override fun onMessage(message: String?) {
                    Log.d(TAG, "Received: $message")
                    message?.let {
                        try {
                            val response = gson.fromJson(it, WebSocketResponse::class.java)
                            onMessageReceived(response)
                        } catch (e: Exception) {
                            Log.e(TAG, "Error parsing message: $e")
                        }
                    }
                }
                
                override fun onClose(code: Int, reason: String?, remote: Boolean) {
                    Log.d(TAG, "WebSocket Closed: $code - $reason")
                    isConnected = false
                    onConnectionChanged(false)
                }
                
                override fun onError(ex: Exception?) {
                    Log.e(TAG, "WebSocket Error: ${ex?.message}")
                    isConnected = false
                    onConnectionChanged(false)
                }
            }
            
            webSocketClient?.connect()
            
        } catch (e: Exception) {
            Log.e(TAG, "Connection error: ${e.message}")
            onConnectionChanged(false)
        }
    }
    
    fun sendMessage(content: String) {
        try {
            val message = WebSocketMessage(content)
            val json = gson.toJson(message)
            
            if (isConnected) {
                webSocketClient?.send(json)
                Log.d(TAG, "Sent: $json")
            } else {
                // Queue message for when connection is restored
                messageQueue.offer(json)
                Log.d(TAG, "Queued message: $json")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error sending message: ${e.message}")
        }
    }
    
    fun disconnect() {
        try {
            webSocketClient?.close()
            isConnected = false
        } catch (e: Exception) {
            Log.e(TAG, "Error disconnecting: ${e.message}")
        }
    }
    
    fun reconnect() {
        disconnect()
        // Wait a moment before reconnecting
        Thread.sleep(1000)
        connect()
    }
}