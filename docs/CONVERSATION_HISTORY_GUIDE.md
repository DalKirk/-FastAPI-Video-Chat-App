# ?? Claude Conversation History - User Guide

## ? What Changed

Your `ClaudeClient` now supports **conversation history** while remaining **100% backward compatible** with existing code.

---

## ?? Overview

### **Before (Still Works)**
```python
claude = get_claude_client()
response = claude.generate_response("Hello!")
# Each call is independent, no memory
```

### **After (New Feature)**
```python
claude = get_claude_client()

# Start a conversation
response1 = claude.generate_response("My name is Alice", conversation_id="user_123")
response2 = claude.generate_response("What's my name?", conversation_id="user_123")
# Claude remembers: "Your name is Alice"
```

---

## ?? Quick Start

### **1. Basic Conversation**

```python
from utils.claude_client import get_claude_client

claude = get_claude_client()

# Use a unique conversation_id for each user or session
user_id = "user_123"

# First message
response1 = claude.generate_response(
    "Hello! My favorite color is blue.",
    conversation_id=user_id
)

# Second message - Claude remembers!
response2 = claude.generate_response(
    "What's my favorite color?",
    conversation_id=user_id
)
# Response: "Your favorite color is blue."
```

### **2. Multiple Conversations**

```python
# Different users have separate conversations
response_alice = claude.generate_response(
    "I love pizza",
    conversation_id="alice_123"
)

response_bob = claude.generate_response(
    "I love tacos",
    conversation_id="bob_456"
)

# Each conversation is independent
claude.generate_response("What do I love?", conversation_id="alice_123")  # "pizza"
claude.generate_response("What do I love?", conversation_id="bob_456")    # "tacos"
```

---

## ?? Use Cases

### **Use Case 1: Chat Room Conversations**

```python
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    claude = get_claude_client()
    conversation_id = f"{room_id}_{user_id}"  # Unique per user per room
    
    while True:
        data = await websocket.receive_text()
        message_data = json.loads(data)
        
        # Use conversation history for this user in this room
        ai_response = claude.generate_response(
            message_data["content"],
            conversation_id=conversation_id
        )
        
        await websocket.send_text(json.dumps({
            "type": "ai_response",
            "content": ai_response
        }))
```

### **Use Case 2: Customer Support Bot**

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/support/chat")
async def support_chat(user_id: str, message: str):
    claude = get_claude_client()
    
    # Maintain support conversation per customer
    response = claude.generate_response(
        message,
        conversation_id=f"support_{user_id}",
        system_prompt="You are a helpful customer support agent."
    )
    
    return {"response": response}
```

### **Use Case 3: AI Tutor with Context**

```python
@app.post("/tutor/ask")
async def ask_tutor(student_id: str, question: str, subject: str):
    claude = get_claude_client()
    
    response = claude.generate_response(
        question,
        conversation_id=f"tutor_{student_id}_{subject}",
        system_prompt=f"You are a {subject} tutor. Help the student learn step by step."
    )
    
    return {"answer": response}
```

---

## ??? API Reference

### **generate_response()**

```python
def generate_response(
    prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    conversation_id: Optional[str] = None  # NEW!
) -> str:
```

**Parameters:**
- `prompt` - User's message
- `max_tokens` - Maximum response length (default: 1000)
- `temperature` - Creativity (0-1, default: 0.7)
- `system_prompt` - System instructions (optional)
- `conversation_id` - **NEW**: Unique ID to track conversation history (optional)

**Returns:** Claude's response as a string

**Behavior:**
- If `conversation_id` is provided ? maintains history
- If `conversation_id` is None ? independent message (backward compatible)

---

### **clear_conversation()**

```python
def clear_conversation(conversation_id: str) -> None:
```

Clear all history for a specific conversation.

**Example:**
```python
# User wants to start fresh
claude.clear_conversation("user_123")
```

---

### **get_conversation_history()**

```python
def get_conversation_history(conversation_id: str) -> List[Dict]:
```

Get the full conversation history.

**Returns:**
```python
[
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "I don't have access to weather data..."}
]
```

**Example:**
```python
history = claude.get_conversation_history("user_123")
print(f"Messages in conversation: {len(history)}")
```

---

### **get_conversation_count()**

```python
def get_conversation_count(conversation_id: str) -> int:
```

Get number of messages in a conversation.

**Example:**
```python
count = claude.get_conversation_count("user_123")
if count > 20:
    claude.clear_conversation("user_123")  # Reset long conversations
```

---

## ?? Complete Example: Multi-User Chat with Memory

```python
from fastapi import FastAPI, WebSocket
from utils.claude_client import get_claude_client
import json

app = FastAPI()
claude = get_claude_client()

@app.websocket("/ws/chat/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    # Each user gets their own conversation
    conversation_id = f"chat_{user_id}"
    
    # Welcome message with context
    welcome = claude.generate_response(
        "A new user just joined. Greet them warmly!",
        conversation_id=conversation_id,
        system_prompt="You are a friendly chat assistant."
    )
    await websocket.send_text(json.dumps({"message": welcome}))
    
    try:
        while True:
            # Receive user message
            data = await websocket.receive_text()
            user_message = json.loads(data)["message"]
            
            # Check conversation length
            if claude.get_conversation_count(conversation_id) > 50:
                # Summarize and start fresh
                history = claude.get_conversation_history(conversation_id)
                summary = f"Previous conversation summary: {len(history)} messages exchanged"
                claude.clear_conversation(conversation_id)
                
                # Start new conversation with summary
                response = claude.generate_response(
                    f"{summary}\n\nUser says: {user_message}",
                    conversation_id=conversation_id
                )
            else:
                # Continue conversation normally
                response = claude.generate_response(
                    user_message,
                    conversation_id=conversation_id
                )
            
            # Send AI response
            await websocket.send_text(json.dumps({
                "message": response,
                "conversation_messages": claude.get_conversation_count(conversation_id)
            }))
            
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Optional: clear conversation on disconnect
        # claude.clear_conversation(conversation_id)
        pass
```

---

## ?? Important Notes

### **1. Backward Compatibility**
All existing code continues to work without changes:
```python
# Still works exactly as before
claude.moderate_content("test")
claude.detect_spam("test")
claude.summarize_conversation(messages)
claude.suggest_reply(context, message)
```

### **2. Memory Management**
Conversations are stored in memory. Consider:
- Clear old conversations periodically
- Limit conversation length (e.g., last 50 messages)
- Use unique IDs per user/session

```python
# Good practice: periodic cleanup
import time

def cleanup_old_conversations():
    # Clear conversations older than 1 hour
    # (You'd need to track timestamps yourself)
    pass
```

### **3. Conversation IDs**
Use meaningful, unique IDs:
```python
# ? Good
conversation_id = f"user_{user_id}"
conversation_id = f"room_{room_id}_user_{user_id}"
conversation_id = f"session_{session_id}"

# ? Avoid
conversation_id = "chat"  # All users share same conversation!
```

### **4. Content Moderation**
Moderation does NOT use conversation history (each check is independent):
```python
# Moderation is always stateless
moderation = claude.moderate_content("some message")
# No history is saved or used
```

---

## ?? Testing

```python
# test_conversation_history.py
from utils.claude_client import get_claude_client

def test_conversation_memory():
    claude = get_claude_client()
    conv_id = "test_123"
    
    # Clear any existing conversation
    claude.clear_conversation(conv_id)
    
    # Test 1: Claude remembers user's name
    response1 = claude.generate_response(
        "My name is Alice and I'm 25 years old.",
        conversation_id=conv_id
    )
    
    response2 = claude.generate_response(
        "What's my name and age?",
        conversation_id=conv_id
    )
    
    print(f"Response: {response2}")
    assert "Alice" in response2
    assert "25" in response2
    
    # Test 2: Get history
    history = claude.get_conversation_history(conv_id)
    assert len(history) == 4  # 2 user + 2 assistant messages
    
    # Test 3: Clear and verify
    claude.clear_conversation(conv_id)
    assert claude.get_conversation_count(conv_id) == 0
    
    print("? All tests passed!")

if __name__ == "__main__":
    test_conversation_memory()
```

---

## ?? Best Practices

### **1. Use Meaningful IDs**
```python
# Per-user conversations
conversation_id = f"user_{user_id}"

# Per-room per-user
conversation_id = f"room_{room_id}_user_{user_id}"

# Per-session
conversation_id = f"session_{session_token}"
```

### **2. Limit Conversation Length**
```python
MAX_MESSAGES = 50

if claude.get_conversation_count(conv_id) > MAX_MESSAGES:
    # Option A: Clear completely
    claude.clear_conversation(conv_id)
    
    # Option B: Summarize first
    history = claude.get_conversation_history(conv_id)
    summary = summarize_and_save(history)
    claude.clear_conversation(conv_id)
```

### **3. Handle Errors Gracefully**
```python
try:
    response = claude.generate_response(
        user_message,
        conversation_id=conv_id
    )
except Exception as e:
    # If error, clear conversation and retry
    claude.clear_conversation(conv_id)
    response = "Sorry, let's start over. What can I help with?"
```

### **4. Clean Up on User Disconnect**
```python
@app.websocket("/ws/{user_id}")
async def websocket(websocket: WebSocket, user_id: str):
    conv_id = f"user_{user_id}"
    try:
        # ... handle messages ...
        pass
    finally:
        # Clean up when user disconnects
        claude.clear_conversation(conv_id)
```

---

## ?? Monitoring

Track conversation usage:

```python
@app.get("/admin/claude-stats")
async def get_claude_stats():
    claude = get_claude_client()
    model_info = claude.get_model_info()
    
    return {
        "active_conversations": model_info["active_conversations"],
        "model": model_info["active_model"],
        "enabled": model_info["is_enabled"]
    }
```

---

## ? Summary

- ? Conversation history is **opt-in** via `conversation_id` parameter
- ? **100% backward compatible** - all existing code works unchanged
- ? Separate conversations per user/session with unique IDs
- ? Methods to manage history: `clear_conversation()`, `get_conversation_history()`, `get_conversation_count()`
- ? Content moderation remains stateless (no history)
- ? Memory efficient - conversations stored in RAM, cleared on demand

**Your existing code needs NO changes. New feature is ready to use!** ??
