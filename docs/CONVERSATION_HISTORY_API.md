# ?? Conversation History API - Complete Reference

## ? What Was Updated

Your FastAPI backend now supports conversation history tracking across **all AI endpoints**. Claude AI will remember previous messages when you provide a `conversation_id`.

---

## ?? Updated Endpoints

### **1. Main Chat Endpoint** `/api/v1/chat`

#### **Without Conversation History (Existing Behavior)**
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What is FastAPI?",
  "conversation_history": []
}
```

**Response:**
```json
{
  "content": "FastAPI is a modern web framework...",
  "format_type": "structured",
  "metadata": {...},
  "success": true,
  "conversation_id": null,
  "conversation_length": 0
}
```

#### **With Conversation History (NEW)**
```bash
POST /api/v1/chat
Content-Type: application/json

{
  "message": "What's my favorite color?",
  "conversation_id": "user_alice_123",
  "conversation_history": []
}
```

**Response:**
```json
{
  "content": "Based on our conversation, your favorite color is blue.",
  "format_type": "conversational",
  "metadata": {...},
  "success": true,
  "conversation_id": "user_alice_123",
  "conversation_length": 4
}
```

---

### **2. AI Generate Endpoint** `/ai/generate`

#### **Without History**
```bash
POST /ai/generate
Content-Type: application/json

{
  "prompt": "Tell me a joke",
  "max_tokens": 100,
  "temperature": 0.8
}
```

#### **With History (NEW)**
```bash
POST /ai/generate
Content-Type: application/json

{
  "prompt": "Tell me another one",
  "max_tokens": 100,
  "temperature": 0.8,
  "conversation_id": "session_xyz_789"
}
```

**Response:**
```json
{
  "response": "Here's another joke...",
  "model": "claude-sonnet-4-5-20250929",
  "conversation_id": "session_xyz_789",
  "conversation_length": 6,
  "debug_info": {...}
}
```

---

### **3. Clear Conversation** `/api/v1/chat/conversation/clear`

```bash
POST /api/v1/chat/conversation/clear?conversation_id=user_123
```

**Response:**
```json
{
  "success": true,
  "message": "Conversation history cleared for: user_123"
}
```

---

### **4. Get Conversation History** `/api/v1/chat/conversation/{conversation_id}/history`

```bash
GET /api/v1/chat/conversation/user_123/history
```

**Response:**
```json
{
  "conversation_id": "user_123",
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "What's my name?"},
    {"role": "assistant", "content": "Your name is Alice."}
  ],
  "message_count": 4
}
```

---

### **5. AI Endpoints with Conversation History**

All AI endpoints now support `conversation_id`:

| Endpoint | Supports History | Parameter |
|----------|------------------|-----------|
| `/api/v1/chat` | ? Yes | `conversation_id` |
| `/ai/generate` | ? Yes | `conversation_id` |
| `/ai/suggest-reply` | ? Yes | `conversation_id` |
| `/ai/conversation/clear` | ? Yes | Required |
| `/ai/conversation/{id}/history` | ? Yes | Path param |
| `/ai/conversation/{id}/count` | ? Yes | Path param |
| `/ai/moderate` | ? No | N/A (stateless) |
| `/ai/detect-spam` | ? No | N/A (stateless) |

---

## ?? Usage Examples

### **Example 1: Multi-Turn Chat Conversation**

```javascript
// Frontend code
const conversationId = `user_${userId}`;

// First message
const response1 = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "My name is Alice and I love coding",
    conversation_id: conversationId
  })
});

// Second message - Claude remembers!
const response2 = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: "What do I love to do?",
    conversation_id: conversationId
  })
});
// Response: "You love coding!"
```

---

### **Example 2: Room-Based Conversations**

```javascript
// Each user in each room gets their own conversation
const conversationId = `room_${roomId}_user_${userId}`;

async function sendMessage(message) {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      room_id: roomId,
      user_id: userId
    })
  });
  
  const data = await response.json();
  
  console.log(`Conversation length: ${data.conversation_length} messages`);
  return data.content;
}
```

---

### **Example 3: Clear Old Conversations**

```javascript
// Clear conversation when user leaves
async function clearConversation(conversationId) {
  await fetch(`/api/v1/chat/conversation/clear?conversation_id=${conversationId}`, {
    method: 'POST'
  });
}

// Or check length and clear if too long
async function checkAndClear(conversationId) {
  const response = await fetch(`/ai/conversation/${conversationId}/count`);
  const data = await response.json();
  
  if (data.message_count > 50) {
    await clearConversation(conversationId);
  }
}
```

---

### **Example 4: View Conversation History**

```javascript
// Get full conversation history
async function getHistory(conversationId) {
  const response = await fetch(`/api/v1/chat/conversation/${conversationId}/history`);
  const data = await response.json();
  
  console.log(`Conversation has ${data.message_count} messages`);
  
  data.messages.forEach(msg => {
    console.log(`${msg.role}: ${msg.content}`);
  });
}
```

---

## ?? Conversation ID Patterns

### **User-Based**
```javascript
const conversationId = `user_${userId}`;
// Example: "user_alice_123"
```

### **Room-Based**
```javascript
const conversationId = `room_${roomId}_user_${userId}`;
// Example: "room_general_user_alice_123"
```

### **Session-Based**
```javascript
const conversationId = `session_${sessionToken}`;
// Example: "session_xyz789abc"
```

### **Feature-Based**
```javascript
const conversationId = `support_${ticketId}`;
// Example: "support_ticket_456"
```

---

## ?? Health Check Updates

### **GET `/api/v1/chat/health`**

**Response (Updated):**
```json
{
  "status": "healthy",
  "claude_enabled": true,
  "active_conversations": 12,
  "services": {
    "context_analyzer": "ready",
    "format_selector": "ready",
    "response_formatter": "ready"
  },
  "features": [
    "context_aware_responses",
    "markdown_formatting",
    "conversation_history"
  ]
}
```

### **GET `/ai/health`**

**Response (Updated):**
```json
{
  "ai_enabled": true,
  "model": "claude-sonnet-4-5-20250929",
  "fallback_model": "claude-3-5-sonnet-20241022",
  "active_conversations": 12,
  "features": [
    "content_moderation",
    "spam_detection",
    "conversation_summary",
    "smart_replies",
    "ai_generation",
    "conversation_history"
  ]
}
```

---

## ?? Deployment

### **Files Modified:**
1. ? `utils/claude_client.py` - Core conversation tracking
2. ? `utils/ai_endpoints.py` - Updated AI endpoints
3. ? `app/models/chat_models.py` - Updated models
4. ? `services/ai_service.py` - Updated service layer
5. ? `api/routes/chat.py` - Updated chat router

### **Backward Compatibility:**
- ? All existing code works unchanged
- ? `conversation_id` is optional everywhere
- ? Default behavior unchanged

---

## ?? Testing

### **Test 1: Basic Conversation**
```bash
# First message
curl -X POST https://your-railway-app.up.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My favorite color is blue",
    "conversation_id": "test_001"
  }'

# Second message
curl -X POST https://your-railway-app.up.railway.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my favorite color?",
    "conversation_id": "test_001"
  }'
```

### **Test 2: Get History**
```bash
curl https://your-railway-app.up.railway.app/api/v1/chat/conversation/test_001/history
```

### **Test 3: Clear Conversation**
```bash
curl -X POST https://your-railway-app.up.railway.app/api/v1/chat/conversation/clear?conversation_id=test_001
```

---

## ?? Best Practices

### **1. Use Meaningful IDs**
```javascript
// ? Good
const conversationId = `user_${userId}_room_${roomId}`;

// ? Bad
const conversationId = "chat";  // All users share same memory!
```

### **2. Clean Up Periodically**
```javascript
// Clear when user disconnects
websocket.onclose = async () => {
  await fetch(`/api/v1/chat/conversation/clear?conversation_id=${conversationId}`, {
    method: 'POST'
  });
};
```

### **3. Limit Conversation Length**
```javascript
// Check and reset if too long
const { conversation_length } = await response.json();

if (conversation_length > 50) {
  await clearConversation(conversationId);
}
```

### **4. Handle Errors**
```javascript
try {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: userInput,
      conversation_id: conversationId
    })
  });
  
  if (!response.ok) {
    // Clear and retry if error
    await clearConversation(conversationId);
  }
} catch (error) {
  console.error('Chat error:', error);
}
```

---

## ?? Request/Response Schemas

### **ChatRequest (Updated)**
```typescript
interface ChatRequest {
  message: string;
  conversation_history?: Message[];
  user_id?: string;
  room_id?: string;
  conversation_id?: string;  // NEW
}
```

### **ChatResponse (Updated)**
```typescript
interface ChatResponse {
  content: string;
  format_type: string;
  metadata: object;
  success: boolean;
  conversation_id?: string;      // NEW
  conversation_length: number;   // NEW
}
```

### **AIRequest (Updated)**
```typescript
interface AIRequest {
  prompt: string;
  max_tokens?: number;
  temperature?: number;
  conversation_id?: string;  // NEW
}
```

---

## ? Summary

**What Changed:**
- ? Added `conversation_id` parameter to all AI endpoints
- ? Added conversation management endpoints
- ? Updated response schemas to include conversation info
- ? Added conversation count to health checks
- ? 100% backward compatible

**How to Use:**
1. **Optional**: Add `conversation_id` to any AI request
2. **Claude Remembers**: Same ID = same conversation memory
3. **Manage**: Use clear/history endpoints as needed

**Your backend is ready for conversation-aware AI interactions!** ??

---

**Last Updated:** January 2025  
**Status:** ? Ready to Deploy  
**Backward Compatible:** Yes
