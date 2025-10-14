package com.yourcompany.chatapp.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.yourcompany.chatapp.databinding.ItemRoomBinding
import com.yourcompany.chatapp.models.Room

class RoomAdapter(
    private val rooms: List<Room>,
    private val onRoomClick: (Room) -> Unit
) : RecyclerView.Adapter<RoomAdapter.RoomViewHolder>() {
    
    class RoomViewHolder(private val binding: ItemRoomBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(room: Room, onRoomClick: (Room) -> Unit) {
            binding.textViewRoomName.text = room.name
            binding.textViewUserCount.text = "${room.users.size} users"
            
            binding.root.setOnClickListener {
                onRoomClick(room)
            }
        }
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RoomViewHolder {
        val binding = ItemRoomBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return RoomViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: RoomViewHolder, position: Int) {
        holder.bind(rooms[position], onRoomClick)
    }
    
    override fun getItemCount(): Int = rooms.size
}