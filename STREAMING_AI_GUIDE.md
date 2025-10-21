# ?? Claude AI Streaming API - Complete Guide

## ?? What is Streaming?

Instead of waiting for the entire response, streaming sends text **as it's generated**, creating a ChatGPT-like typing effect.

---

## ?? Backend Setup (FastAPI)

### **1. Add Streaming Router to main.py**

```python
# In main.py, add this import
from utils.streaming_ai_endpoints import streaming_ai_router

# Add the router
app.include_router(streaming_ai_router)
```

### **2. Endpoints Available**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ai/stream/chat` | POST | Multi-turn conversations |
| `/ai/stream/generate` | POST | Simple text generation |
| `/ai/stream/health` | GET | Check streaming status |

---

## ?? Frontend Integration

### **React/Next.js Example**

```typescript
// app/api/chat/route.ts (Next.js 14)
import { StreamingTextResponse } from 'ai';

export async function POST(req: Request) {
  const { messages } = await req.json();
  
  const response = await fetch('https://your-railway-app.up.railway.app/ai/stream/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      messages,
      max_tokens: 2048,
      temperature: 0.7
    }),
  });

  // Return streaming response
  return new StreamingTextResponse(response.body);
}
```

### **Vanilla JavaScript Example**

```javascript
async function streamChatResponse(prompt) {
  const eventSource = new EventSource(
    'https://your-railway-app.up.railway.app/ai/stream/generate',
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        max_tokens: 1000,
        temperature: 0.7
      })
    }
  );

  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'content') {
      // Append text to UI
      document.getElementById('response').textContent += data.text;
    } else if (data.type === 'done') {
      console.log('Streaming complete. Model:', data.model);
      eventSource.close();
    } else if (data.type === 'error') {
      console.error('Streaming error:', data.error);
      eventSource.close();
    }
  };

  eventSource.onerror = (error) => {
    console.error('EventSource failed:', error);
    eventSource.close();
  };
}

// Usage
streamChatResponse("Tell me a short story about a robot");
```

### **Using fetch() with ReadableStream**

```javascript
async function streamWithFetch(prompt) {
  const response = await fetch('https://your-railway-app.up.railway.app/ai/stream/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: prompt,
      max_tokens: 1000,
      temperature: 0.7
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    
    if (done) break;
    
    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        if (data.type === 'content') {
          // Update UI with new text
          displayText(data.text);
        } else if (data.type === 'done') {
          console.log('Stream complete');
        }
      }
    }
  }
}
```

---

## ?? Testing with cURL

### **Test Simple Generation**

```bash
curl -N -X POST https://your-railway-app.up.railway.app/ai/stream/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a haiku about coding",
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

### **Test Chat Conversation**

```bash
curl -N -X POST https://your-railway-app.up.railway.app/ai/stream/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is FastAPI?"}
    ],
    "max_tokens": 500
  }'
```

### **Test Health Check**

```bash
curl https://your-railway-app.up.railway.app/ai/stream/health
```

**Expected Response:**
```json
{
  "streaming_enabled": true,
  "model": "claude-sonnet-4-5-20250929",
  "supports_streaming": true,
  "format": "Server-Sent Events (SSE)"
}
```

---

## ?? Event Types

Your streaming API sends these event types:

### **1. Content Event**
```json
{
  "type": "content",
  "text": "This is a "
}
```

### **2. Done Event**
```json
{
  "type": "done",
  "model": "claude-sonnet-4-5-20250929"
}
```

### **3. Error Event**
```json
{
  "type": "error",
  "error": "Rate limit exceeded"
}
```

---

## ?? Complete React Component Example

```typescript
'use client';

import { useState } from 'react';

export default function StreamingChat() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  const handleStream = async () => {
    setResponse('');
    setIsStreaming(true);

    const res = await fetch('/api/stream-generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: input })
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader!.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          if (data.type === 'content') {
            setResponse((prev) => prev + data.text);
          }
        }
      }
    }

    setIsStreaming(false);
  };

  return (
    <div className="p-4">
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className="w-full p-2 border rounded"
        placeholder="Ask Claude anything..."
      />
      <button
        onClick={handleStream}
        disabled={isStreaming}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        {isStreaming ? 'Streaming...' : 'Send'}
      </button>
      <div className="mt-4 p-4 border rounded whitespace-pre-wrap">
        {response || 'Response will appear here...'}
      </div>
    </div>
  );
}
```

---

## ?? Deployment

### **Railway Configuration**

? **Already Configured** - Your FastAPI app on Railway supports streaming out of the box.

No special configuration needed! The streaming endpoints work automatically.

### **Vercel Frontend Configuration**

If using Vercel, add to `next.config.js`:

```javascript
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/stream/:path*',
        destination: 'https://your-railway-app.up.railway.app/ai/stream/:path*'
      }
    ];
  }
};
```

---

## ?? Request/Response Formats

### **Chat Request**

```json
{
  "messages": [
    {"role": "user", "content": "Hello!"},
    {"role": "assistant", "content": "Hi there!"},
    {"role": "user", "content": "How are you?"}
  ],
  "max_tokens": 2048,
  "temperature": 0.7,
  "system": "You are a helpful assistant"
}
```

### **Generate Request**

```json
{
  "prompt": "Write a poem about the ocean",
  "max_tokens": 500,
  "temperature": 0.8,
  "system_prompt": "You are a creative poet"
}
```

---

## ? Performance Tips

1. **Use appropriate max_tokens** - Lower = faster
2. **Temperature affects speed** - Lower = faster
3. **Buffer chunks on frontend** - Smooth rendering
4. **Handle reconnection** - Network issues gracefully
5. **Show loading state** - Better UX

---

## ?? Troubleshooting

### **Issue: No streaming, entire response at once**

**Solution:** Check that you're using `StreamingResponse` and SSE format.

### **Issue: CORS errors**

**Solution:** Add streaming endpoints to CORS config in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.vercel.app"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
```

### **Issue: Connection timeout**

**Solution:** Adjust Railway timeout settings or reduce `max_tokens`.

---

## ? Integration Checklist

- [ ] Add `streaming_ai_endpoints.py` to your project
- [ ] Import router in `main.py`
- [ ] Test streaming health endpoint
- [ ] Implement frontend streaming handler
- [ ] Test with cURL
- [ ] Deploy to Railway
- [ ] Test from frontend
- [ ] Add error handling

---

## ?? Summary

**What You Get:**

? **Real-time streaming** - ChatGPT-like experience  
? **Multi-turn conversations** - Full chat support  
? **Simple prompts** - Quick text generation  
? **Automatic fallback** - Switches models if needed  
? **Date context** - Claude knows current time  
? **Error handling** - Graceful error recovery  

**Your FastAPI app now has production-ready Claude AI streaming!** ??

---

**Last Updated:** January 20, 2025  
**Claude Model:** claude-sonnet-4-5-20250929  
**Streaming Protocol:** Server-Sent Events (SSE)
