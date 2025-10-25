# Integration Guide for AI Chat Service

## Overview
This guide shows how to integrate the context-aware AI chat service into your FastAPI application.

## Architecture

```
???????????????????
?   API Endpoint  ?  (api/routes/chat.py)
???????????????????
         ?
???????????????????
?   AI Service    ?  (services/ai_service.py)
???????????????????
         ?
    ???????????????????????????????????????
    ?         ?            ?              ?
???????? ???????? ???????????? ????????????????
? Ctx  ? ? Fmt  ? ?  Resp    ? ? Claude API   ?
? Anlz ? ? Sel  ? ?  Fmtr    ? ?   Client     ?
???????? ???????? ???????????? ????????????????
```

## Integration Steps

### 1. Update main.py

Add the chat router to your main FastAPI app:

```python
from fastapi import FastAPI
from api.routes.chat import router as chat_router

app = FastAPI(
    title="FastAPI Video Chat with AI",
    version="2.0.0"
)

# Include the AI chat router
app.include_router(chat_router)

# ... your existing routes ...
```

### 2. Test the Endpoint

**Health Check:**
```bash
curl http://localhost:8000/api/v1/chat/health
```

**Chat Request:**
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I use FastAPI?",
    "conversation_history": []
  }'
```

**Response:**
```json
{
  "content": "## Using FastAPI\n\nFastAPI is a modern...",
  "format_type": "structured",
  "metadata": {
    "is_casual": false,
    "is_technical": true,
    "needs_structure": true,
    "is_emotional": false,
    "needs_code": false,
    "conversation_tone": "technical"
  },
  "success": true
}
```

## Frontend Integration

### Example with fetch:

```typescript
async function sendMessage(message: string, history: Message[]) {
  const response = await fetch('/api/v1/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_history: history,
    }),
  });

  const data = await response.json();
  return data.content; // Already formatted markdown
}
```

### Example with React:

```tsx
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  const handleSend = async () => {
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
        conversation_history: messages,
      }),
    });

    const data = await response.json();
    
    setMessages([
      ...messages,
      { role: 'user', content: input },
      { role: 'assistant', content: data.content }
    ]);
    setInput('');
  };

  return (
    <div>
      {messages.map((msg, i) => (
        <ReactMarkdown key={i}>{msg.content}</ReactMarkdown>
      ))}
      <input value={input} onChange={(e) => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </div>
  );
}
```

## Configuration

### Environment Variables

Ensure these are set in your `.env`:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

### Customization

You can customize the AI behavior by modifying:

- **Context Analysis** (`services/context_analyzer.py`):
  - Add new context detection methods
  - Adjust keyword lists for detection

- **Format Selection** (`services/format_selector.py`):
  - Add new format types
  - Modify format selection logic
  - Customize format rules

- **Response Formatting** (`services/response_formatter.py`):
  - Add new formatting methods
  - Adjust markdown generation rules

## Error Handling

The service includes multiple layers of error handling:

1. **AI Service Level**: Returns fallback responses on failure
2. **API Endpoint Level**: Returns proper HTTP error codes
3. **Quality Checks**: Validates responses before returning

## Monitoring

Check service health:
```bash
curl http://localhost:8000/api/v1/chat/health
```

Expected response:
```json
{
  "status": "healthy",
  "claude_enabled": true,
  "services": {
    "context_analyzer": "ready",
    "format_selector": "ready",
    "response_formatter": "ready"
  }
}
```

## Performance Tips

1. The `AIService` is initialized as a singleton to avoid repeated setup
2. Use dependency injection (`Depends(get_ai_service)`) for proper lifecycle management
3. Claude API calls are async for better concurrency
4. Response formatting is done server-side to reduce client load

## Troubleshooting

**Issue: "Claude AI is not configured"**
- Solution: Check that `ANTHROPIC_API_KEY` is set in environment variables

**Issue: Response takes too long**
- Solution: Reduce `max_tokens` in `ai_service.py` (default: 2048)

**Issue: Formatting not applied**
- Solution: Check that format rules are being passed correctly through the pipeline

## Next Steps

- Add rate limiting to the chat endpoint
- Implement conversation history persistence
- Add user authentication
- Set up caching for common queries
- Add metrics and logging
