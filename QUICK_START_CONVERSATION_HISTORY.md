# ?? Quick Start: Claude Conversation History

## ? Feature is Ready!

Your Claude AI client now remembers conversation history. **No code changes needed to existing functionality.**

---

## ?? Basic Usage

### **Example 1: Simple Conversation**

```python
from utils.claude_client import get_claude_client

# Get the client
claude = get_claude_client()

# Start a conversation with a unique ID
user_id = "alice_123"

# First message
response1 = claude.generate_response(
    "Hi! My favorite food is sushi.",
    conversation_id=user_id  # ? This enables memory
)
print(response1)

# Second message - Claude remembers!
response2 = claude.generate_response(
    "What's my favorite food?",
    conversation_id=user_id  # ? Same ID = same conversation
)
print(response2)  # "Your favorite food is sushi."
```

---

## ?? Usage Patterns

### **Pattern 1: User-Based Conversations**

```python
@app.post("/chat")
async def chat(user_id: str, message: str):
    claude = get_claude_client()
    
    response = claude.generate_response(
        message,
        conversation_id=f"user_{user_id}"  # Each user gets their own memory
    )
    
    return {"response": response}
```

### **Pattern 2: Session-Based Conversations**

```python
@app.post("/support")
async def support_chat(session_id: str, message: str):
    claude = get_claude_client()
    
    response = claude.generate_response(
        message,
        conversation_id=f"session_{session_id}",  # Track by session
        system_prompt="You are a helpful customer support agent."
    )
    
    return {"response": response}
```

### **Pattern 3: Room-Based Conversations**

```python
@app.websocket("/ws/{room_id}/{user_id}")
async def chat_room(websocket: WebSocket, room_id: str, user_id: str):
    claude = get_claude_client()
    
    # Each user in each room gets separate memory
    conversation_id = f"room_{room_id}_user_{user_id}"
    
    while True:
        message = await websocket.receive_text()
        
        response = claude.generate_response(
            message,
            conversation_id=conversation_id
        )
        
        await websocket.send_text(response)
```

---

## ??? Management

### **Check Conversation Length**

```python
# Get message count
count = claude.get_conversation_count("user_123")
print(f"Messages in conversation: {count}")
```

### **View Conversation History**

```python
# Get all messages
history = claude.get_conversation_history("user_123")

for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### **Clear Conversation**

```python
# Start fresh
claude.clear_conversation("user_123")
```

---

## ? Complete Example

```python
from utils.claude_client import get_claude_client
from fastapi import FastAPI, WebSocket

app = FastAPI()
claude = get_claude_client()

@app.websocket("/ws/chat/{user_id}")
async def chat(websocket: WebSocket, user_id: str):
    await websocket.accept()
    conv_id = f"chat_{user_id}"
    
    # Welcome message
    welcome = claude.generate_response(
        "A new user just joined. Greet them!",
        conversation_id=conv_id
    )
    await websocket.send_text(welcome)
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_text()
            
            # Check if conversation is too long
            if claude.get_conversation_count(conv_id) > 50:
                # Clear and inform user
                claude.clear_conversation(conv_id)
                await websocket.send_text("Starting fresh conversation...")
            
            # Get AI response with memory
            response = claude.generate_response(
                message,
                conversation_id=conv_id
            )
            
            # Send response
            await websocket.send_text(response)
            
    except WebSocketDisconnect:
        # Clean up when user disconnects
        claude.clear_conversation(conv_id)
```

---

## ?? Key Points

1. **Optional Feature**: Only use `conversation_id` when you want memory
2. **Unique IDs**: Each user/session needs a unique conversation_id
3. **Memory Management**: Clear old conversations to save memory
4. **Backward Compatible**: All existing code works unchanged

---

## ?? Test It!

Run the test script:
```bash
python test_conversation_history.py
```

---

## ?? Documentation

- **Full Guide**: `docs/CONVERSATION_HISTORY_GUIDE.md`
- **Summary**: `CONVERSATION_HISTORY_SUMMARY.md`
- **Test File**: `test_conversation_history.py`

---

## ? You're Ready!

Start using conversation history by adding `conversation_id` to your `generate_response()` calls!

```python
# Without memory (old way - still works)
response = claude.generate_response("Hello")

# With memory (new way)
response = claude.generate_response("Hello", conversation_id="user_123")
```

That's it! ??
