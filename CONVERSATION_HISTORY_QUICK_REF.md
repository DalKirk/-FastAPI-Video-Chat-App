# ?? Quick Reference: Conversation History API

## ?? Basic Usage

```javascript
// Add conversation_id to any AI request for memory
const response = await fetch('/api/v1/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    message: userInput,
    conversation_id: `user_${userId}`  // ? Add this!
  })
});
```

---

## ?? Key Endpoints

| Endpoint | Use Case |
|----------|----------|
| `POST /api/v1/chat` | Chat with memory |
| `POST /ai/generate` | Generate with memory |
| `POST /api/v1/chat/conversation/clear?conversation_id=X` | Clear history |
| `GET /api/v1/chat/conversation/{id}/history` | Get history |

---

## ?? Conversation ID Patterns

```javascript
// User-based
`user_${userId}`

// Room-based
`room_${roomId}_user_${userId}`

// Session-based
`session_${sessionId}`
```

---

## ? Response Format

```json
{
  "content": "AI response here...",
  "format_type": "conversational",
  "success": true,
  "conversation_id": "user_123",
  "conversation_length": 4
}
```

---

## ?? Cleanup Example

```javascript
// Clear when conversation gets too long
if (response.conversation_length > 50) {
  await fetch(`/api/v1/chat/conversation/clear?conversation_id=${conversationId}`, {
    method: 'POST'
  });
}
```

---

## ?? Check Health

```bash
curl https://your-app.up.railway.app/api/v1/chat/health
```

---

## ?? Full Documentation

- `docs/CONVERSATION_HISTORY_API.md` - Complete API reference
- `BACKEND_CONVERSATION_HISTORY_COMPLETE.md` - Implementation summary
- `QUICK_START_CONVERSATION_HISTORY.md` - Quick start guide

---

**That's it! Your backend now remembers conversations.** ??
