package com.yourcompany.chatapp

import android.media.ToneGenerator
import android.media.AudioManager
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.yourcompany.chatapp.adapters.MessageAdapter
import com.yourcompany.chatapp.databinding.ActivityChatBinding
import com.yourcompany.chatapp.models.*
import com.yourcompany.chatapp.network.RetrofitClient
import com.yourcompany.chatapp.network.WebSocketManager
import kotlinx.coroutines.launch

class ChatActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityChatBinding
    private lateinit var messageAdapter: MessageAdapter
    private lateinit var webSocketManager: WebSocketManager
    private lateinit var toneGenerator: ToneGenerator
    
    private val messages = mutableListOf<Message>()
    private var room: Room? = null
    private var user: User? = null
    private var isConnected = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityChatBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // Get data from intent
        room = intent.getParcelableExtra("room")
        user = intent.getParcelableExtra("user")
        
        if (room == null || user == null) {
            Toast.makeText(this, "Invalid room or user data", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        setupViews()
        setupRecyclerView()
        setupWebSocket()
        setupClickListeners()
        loadMessages()
        joinRoom()
        
        // Initialize sound effects
        toneGenerator = ToneGenerator(AudioManager.STREAM_NOTIFICATION, 80)
    }
    
    private fun setupViews() {
        binding.textViewRoomName.text = "Room: ${room?.name}"
        binding.textViewUsername.text = "User: ${user?.username}"
    }
    
    private fun setupRecyclerView() {
        messageAdapter = MessageAdapter(messages, user?.id ?: "")
        
        binding.recyclerViewMessages.apply {
            layoutManager = LinearLayoutManager(this@ChatActivity)
            adapter = messageAdapter
        }
    }
    
    private fun setupWebSocket() {
        webSocketManager = WebSocketManager(
            roomId = room?.id ?: "",
            userId = user?.id ?: "",
            onMessageReceived = { response ->
                runOnUiThread {
                    handleWebSocketMessage(response)
                }
            },
            onConnectionChanged = { connected ->
                runOnUiThread {
                    isConnected = connected
                    updateConnectionStatus()
                }
            }
        )
        
        webSocketManager.connect()
    }
    
    private fun setupClickListeners() {
        binding.buttonSend.setOnClickListener {
            sendMessage()
        }
        
        binding.buttonReconnect.setOnClickListener {
            webSocketManager.reconnect()
        }
        
        binding.editTextMessage.setOnEditorActionListener { _, _, _ ->
            sendMessage()
            true
        }
    }
    
    private fun loadMessages() {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.apiService.getRoomMessages(room?.id ?: "")
                if (response.isSuccessful) {
                    messages.clear()
                    response.body()?.let { messages.addAll(it) }
                    messageAdapter.notifyDataSetChanged()
                    scrollToBottom()
                }
            } catch (e: Exception) {
                Toast.makeText(this@ChatActivity, "Error loading messages: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun joinRoom() {
        lifecycleScope.launch {
            try {
                val request = JoinRoomRequest(user?.id ?: "")
                RetrofitClient.apiService.joinRoom(room?.id ?: "", request)
            } catch (e: Exception) {
                // Join room error is not critical for chat functionality
            }
        }
    }
    
    private fun sendMessage() {
        val content = binding.editTextMessage.text.toString().trim()
        if (content.isEmpty()) {
            Toast.makeText(this, "Please enter a message", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (!isConnected) {
            Toast.makeText(this, "Not connected to chat", Toast.LENGTH_SHORT).show()
            return
        }
        
        webSocketManager.sendMessage(content)
        binding.editTextMessage.text.clear()
    }
    
    private fun handleWebSocketMessage(response: WebSocketResponse) {
        when (response.type) {
            "message" -> {
                val message = Message(
                    id = response.id ?: "",
                    user_id = response.user_id ?: "",
                    username = response.username ?: "",
                    room_id = room?.id ?: "",
                    content = response.content ?: "",
                    timestamp = response.timestamp ?: ""
                )
                
                messages.add(message)
                messageAdapter.notifyItemInserted(messages.size - 1)
                scrollToBottom()
                
                // Play message sound
                playSound(ToneGenerator.TONE_PROP_BEEP)
            }
            
            "user_joined" -> {
                addSystemMessage(response.message ?: "User joined")
                playSound(ToneGenerator.TONE_PROP_ACK)
            }
            
            "user_left" -> {
                addSystemMessage(response.message ?: "User left")
                playSound(ToneGenerator.TONE_PROP_NACK)
            }
        }
    }
    
    private fun addSystemMessage(content: String) {
        val systemMessage = Message(
            id = "system_${System.currentTimeMillis()}",
            user_id = "system",
            username = "System",
            room_id = room?.id ?: "",
            content = content,
            timestamp = System.currentTimeMillis().toString()
        )
        
        messages.add(systemMessage)
        messageAdapter.notifyItemInserted(messages.size - 1)
        scrollToBottom()
    }
    
    private fun updateConnectionStatus() {
        binding.textViewConnectionStatus.text = if (isConnected) {
            "🟢 Connected"
        } else {
            "🔴 Disconnected"
        }
        
        binding.buttonReconnect.isEnabled = !isConnected
    }
    
    private fun scrollToBottom() {
        if (messages.isNotEmpty()) {
            binding.recyclerViewMessages.smoothScrollToPosition(messages.size - 1)
        }
    }
    
    private fun playSound(toneType: Int) {
        try {
            toneGenerator.startTone(toneType, 150)
        } catch (e: Exception) {
            // Sound playback failed, continue without sound
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        webSocketManager.disconnect()
        toneGenerator.release()
    }
    
    override fun onPause() {
        super.onPause()
        // Keep WebSocket connection alive in background
    }
    
    override fun onResume() {
        super.onResume()
        if (!isConnected) {
            webSocketManager.reconnect()
        }
    }
}