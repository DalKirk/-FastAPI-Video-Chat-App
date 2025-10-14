package com.yourcompany.chatapp.adapters

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.yourcompany.chatapp.databinding.ItemMessageBinding
import com.yourcompany.chatapp.models.Message
import java.text.SimpleDateFormat
import java.util.*

class MessageAdapter(
    private val messages: List<Message>,
    private val currentUserId: String
) : RecyclerView.Adapter<MessageAdapter.MessageViewHolder>() {
    
    private val dateFormat = SimpleDateFormat("HH:mm", Locale.getDefault())
    
    class MessageViewHolder(private val binding: ItemMessageBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(message: Message, currentUserId: String, dateFormat: SimpleDateFormat) {
            binding.textViewUsername.text = message.username
            binding.textViewMessage.text = message.content
            
            // Format timestamp
            try {
                val timestamp = message.timestamp.toLongOrNull() ?: System.currentTimeMillis()
                binding.textViewTime.text = dateFormat.format(Date(timestamp))
            } catch (e: Exception) {
                binding.textViewTime.text = ""
            }
            
            // Style message based on sender
            if (message.user_id == currentUserId) {
                // Current user's message - align right, different color
                binding.root.setBackgroundColor(0xFF2196F3.toInt())
                binding.textViewUsername.setTextColor(0xFFFFFFFF.toInt())
                binding.textViewMessage.setTextColor(0xFFFFFFFF.toInt())
                binding.textViewTime.setTextColor(0xFFCCCCCC.toInt())
            } else if (message.user_id == "system") {
                // System message - center align, gray color
                binding.root.setBackgroundColor(0xFFF5F5F5.toInt())
                binding.textViewUsername.setTextColor(0xFF666666.toInt())
                binding.textViewMessage.setTextColor(0xFF666666.toInt())
                binding.textViewTime.setTextColor(0xFF999999.toInt())
            } else {
                // Other user's message - default style
                binding.root.setBackgroundColor(0xFFFFFFFF.toInt())
                binding.textViewUsername.setTextColor(0xFF333333.toInt())
                binding.textViewMessage.setTextColor(0xFF000000.toInt())
                binding.textViewTime.setTextColor(0xFF666666.toInt())
            }
        }
    }
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MessageViewHolder {
        val binding = ItemMessageBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return MessageViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: MessageViewHolder, position: Int) {
        holder.bind(messages[position], currentUserId, dateFormat)
    }
    
    override fun getItemCount(): Int = messages.size
}