package com.yourcompany.chatapp

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.yourcompany.chatapp.adapters.RoomAdapter
import com.yourcompany.chatapp.databinding.ActivityMainBinding
import com.yourcompany.chatapp.models.Room
import com.yourcompany.chatapp.models.RoomCreateRequest
import com.yourcompany.chatapp.models.User
import com.yourcompany.chatapp.models.UserCreateRequest
import com.yourcompany.chatapp.network.RetrofitClient
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var roomAdapter: RoomAdapter
    private var currentUser: User? = null
    private val rooms = mutableListOf<Room>()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupRecyclerView()
        setupClickListeners()
        loadRooms()
    }
    
    private fun setupRecyclerView() {
        roomAdapter = RoomAdapter(rooms) { room ->
            joinRoom(room)
        }
        
        binding.recyclerViewRooms.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = roomAdapter
        }
    }
    
    private fun setupClickListeners() {
        binding.buttonCreateUser.setOnClickListener {
            createUser()
        }
        
        binding.buttonCreateRoom.setOnClickListener {
            createRoom()
        }
        
        binding.buttonRefreshRooms.setOnClickListener {
            loadRooms()
        }
    }
    
    private fun createUser() {
        val username = binding.editTextUsername.text.toString().trim()
        if (username.isEmpty()) {
            Toast.makeText(this, "Please enter a username", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.apiService.createUser(UserCreateRequest(username))
                if (response.isSuccessful) {
                    currentUser = response.body()
                    Toast.makeText(this@MainActivity, "User created: ${currentUser?.username}", Toast.LENGTH_SHORT).show()
                    binding.textViewCurrentUser.text = "User: ${currentUser?.username}"
                } else {
                    Toast.makeText(this@MainActivity, "Failed to create user", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun createRoom() {
        val roomName = binding.editTextRoomName.text.toString().trim()
        if (roomName.isEmpty()) {
            Toast.makeText(this, "Please enter a room name", Toast.LENGTH_SHORT).show()
            return
        }
        
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.apiService.createRoom(RoomCreateRequest(roomName))
                if (response.isSuccessful) {
                    Toast.makeText(this@MainActivity, "Room created successfully", Toast.LENGTH_SHORT).show()
                    binding.editTextRoomName.text.clear()
                    loadRooms()
                } else {
                    Toast.makeText(this@MainActivity, "Failed to create room", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun loadRooms() {
        lifecycleScope.launch {
            try {
                val response = RetrofitClient.apiService.getRooms()
                if (response.isSuccessful) {
                    rooms.clear()
                    response.body()?.let { rooms.addAll(it) }
                    roomAdapter.notifyDataSetChanged()
                } else {
                    Toast.makeText(this@MainActivity, "Failed to load rooms", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Error loading rooms: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun joinRoom(room: Room) {
        val user = currentUser
        if (user == null) {
            Toast.makeText(this, "Please create a user first", Toast.LENGTH_SHORT).show()
            return
        }
        
        val intent = Intent(this, ChatActivity::class.java).apply {
            putExtra("room", room)
            putExtra("user", user)
        }
        startActivity(intent)
    }
}