# ?? Claude AI Web Search Integration Guide

## ? Overview

Your FastAPI Video Chat application now has **automatic web search** integrated with Claude AI! When users ask questions about current events, Claude will automatically search the web and provide up-to-date information with source citations.

---

## ?? Features

- ? **Automatic Search Detection** - Detects when queries need current information
- ? **Brave Search API Integration** - Fast, privacy-focused web search
- ? **Smart Keyword Detection** - Recognizes words like "today", "latest", "news", "current"
- ? **Source Citations** - Claude cites sources when using search results
- ? **Graceful Degradation** - Works without search API, just without web results
- ? **Backward Compatible** - Existing code works unchanged

---

## ?? Quick Start

### Step 1: Get a Brave Search API Key

1. Visit: https://brave.com/search/api/
2. Sign up for a free account (1,000 queries/month free)
3. Create an API key
4. Copy your API key

### Step 2: Add to Environment

**Local Development (`.env`):**
```bash
BRAVE_SEARCH_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Railway Production:**
```bash
railway variables set BRAVE_SEARCH_API_KEY=BSAxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Vercel/Other Platforms:**
Add `BRAVE_SEARCH_API_KEY` to your environment variables in the platform dashboard.

---

## ?? How It Works

### Automatic Search Detection

Claude automatically searches when queries contain these keywords:
- **Temporal**: `today`, `now`, `current`, `latest`, `recent`, `this week`, `this month`, `this year`
- **News**: `news`, `what's happening`, `what happened`, `update on`
- **Years**: `2024`, `2025`

### Example Queries That Trigger Search

```python
# These will automatically search the web:
"What's the weather today?"
"Latest news on AI technology"
"What happened this week in sports?"
"Current stock price of Tesla"
"Recent developments in climate change"
```

### Example Queries That DON'T Trigger Search

```python
# These work without search (general knowledge):
"Explain quantum physics"
"How do I write a Python function?"
"What is the capital of France?"
"Tell me a joke"
```

---

## ?? Usage Examples

### Example 1: Basic Web Search

```python
from utils.claude_client import get_claude_client

claude = get_claude_client()

# Automatically searches the web
response = await claude.generate_response(
    "What are the latest developments in AI today?",
    conversation_id="user_123"
)

print(response)
# Claude will use search results and cite sources:
# "According to recent search results from TechCrunch, ..."
```

### Example 2: Disable Search for Specific Queries

```python
# Disable search even if keywords are present
response = await claude.generate_response(
    "What's happening in quantum mechanics?",
    enable_search=False  # Disable web search
)
```

### Example 3: Check Search Status

```python
claude = get_claude_client()

# Check if search is enabled
if claude.is_search_enabled:
    print("? Web search is enabled")
else:
    print("? Web search is disabled (no API key)")

# Get model info including search status
info = claude.get_model_info()
print(f"Search enabled: {info['is_search_enabled']}")
```

---

## ?? API Integration

### FastAPI Endpoint Example

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.claude_client import get_claude_client

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: str
    enable_search: bool = True  # Optional, defaults to True

@router.post("/chat")
async def chat(request: ChatRequest):
    claude = get_claude_client()
    
    if not claude.is_enabled:
        raise HTTPException(status_code=503, detail="AI not configured")
    
    response = await claude.generate_response(
        prompt=request.message,
        conversation_id=request.conversation_id,
        enable_search=request.enable_search
    )
    
    return {
        "response": response,
        "search_enabled": claude.is_search_enabled
    }
```

### WebSocket Example

```python
@app.websocket("/ws/chat/{user_id}")
async def chat_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    claude = get_claude_client()
    
    while True:
        message = await websocket.receive_text()
        
        # Claude automatically searches when needed
        response = await claude.generate_response(
            message,
            conversation_id=f"ws_{user_id}"
        )
        
        await websocket.send_text(response)
```

---

## ?? Frontend Integration

### Example: React Chat Component

```javascript
async function sendMessage(message, conversationId) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      conversation_id: conversationId,
      enable_search: true  // Enable web search
    })
  });
  
  const data = await response.json();
  
  // Show if search was used
  if (data.search_used) {
    console.log('Claude used web search for this response');
  }
  
  return data.response;
}

// Example usage
const reply = await sendMessage(
  "What's the latest news on SpaceX?",
  "user_123"
);
```

---

## ?? Configuration

### Search Parameters

You can customize search behavior in `utils/claude_client.py`:

```python
# In _detect_search_need():
current_indicators = [
    "today", "now", "current", "latest", "recent", "news",
    "this week", "this month", "this year", "2024", "2025",
    "what's happening", "what happened", "update on"
]

# Add your own keywords:
current_indicators.append("breaking")
current_indicators.append("trending")
```

### Search Result Count

```python
# In generate_response():
search_results = await self._search_web(search_query, count=5)

# Change count (max 20):
search_results = await self._search_web(search_query, count=10)
```

---

## ?? Security & Best Practices

### 1. API Key Management

```python
# ? Good - Use environment variables
BRAVE_SEARCH_API_KEY=xxx

# ? Bad - Never hardcode
brave_api_key = "BSAxxxxx"  # DON'T DO THIS
```

### 2. Rate Limiting

Brave Search free tier: 1,000 queries/month

```python
# Add rate limiting for search-heavy endpoints
from middleware.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    requests_limit=10,  # 10 requests per minute
    time_window=60
)
```

### 3. Error Handling

```python
# Search failures are graceful - Claude works without search
try:
    response = await claude.generate_response(prompt)
except Exception as e:
    logger.error(f"Error: {e}")
    # Claude will still work, just without web search
```

### 4. Cache Common Queries

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_search(query: str):
    return await claude.generate_response(query)
```

---

## ?? Monitoring

### Check Search Usage

```python
from utils.claude_client import get_claude_client

claude = get_claude_client()
info = claude.get_model_info()

print(f"""
AI Status:
- Model: {info['active_model']}
- AI Enabled: {info['is_enabled']}
- Search Enabled: {info['is_search_enabled']}
- Active Conversations: {info['active_conversations']}
""")
```

### Logging

Search activity is automatically logged:

```python
# In logs, you'll see:
INFO - Detected search need for: latest news on AI
INFO - Web search for 'latest news on AI' returned 5 results
INFO - Claude response received (len=543, history_length=4, search_used=True)
```

---

## ?? Testing

### Test Search Detection

```python
# test_search.py
from utils.claude_client import get_claude_client
import asyncio

async def test_search():
    claude = get_claude_client()
    
    # Test queries that should trigger search
    queries = [
        "What's the weather today?",
        "Latest news on climate change",
        "What happened this week?"
    ]
    
    for query in queries:
        print(f"\n?? Testing: {query}")
        response = await claude.generate_response(query)
        print(f"?? Response: {response[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_search())
```

### Test Without Search

```python
async def test_no_search():
    claude = get_claude_client()
    
    # Test general knowledge query (no search)
    response = await claude.generate_response(
        "Explain how neural networks work",
        enable_search=False
    )
    
    print(response)
```

---

## ?? Troubleshooting

### Issue: Search Not Working

**Check 1: API Key Set?**
```python
import os
print(os.getenv("BRAVE_SEARCH_API_KEY"))  # Should print your key
```

**Check 2: Search Enabled?**
```python
claude = get_claude_client()
print(claude.is_search_enabled)  # Should be True
```

**Check 3: Search Triggered?**
```python
# Try explicit search keywords
response = await claude.generate_response(
    "What's the latest news today?"  # Should trigger search
)
```

### Issue: "Rate Limit Exceeded"

You've hit Brave's monthly limit. Solutions:
1. Upgrade Brave Search plan
2. Implement caching for common queries
3. Add rate limiting to endpoints

### Issue: Search Results Low Quality

```python
# Increase result count
search_results = await self._search_web(query, count=10)  # More results

# Or refine search keywords in _detect_search_need()
```

---

## ?? Pricing

### Brave Search API Pricing

| Tier | Queries/Month | Price |
|------|---------------|-------|
| Free | 1,000 | $0 |
| Basic | 10,000 | $5/month |
| Pro | 100,000 | $50/month |
| Enterprise | Unlimited | Contact sales |

**Tips to Reduce Costs:**
- Cache search results for 1 hour
- Only enable search for time-sensitive queries
- Use rate limiting
- Monitor usage in Brave dashboard

---

## ?? Advanced Usage

### Custom Search Logic

```python
# Override search detection for specific use cases
def custom_search_detect(prompt: str) -> bool:
    # Your custom logic
    if "stock price" in prompt.lower():
        return True
    if "weather" in prompt.lower():
        return True
    return False
```

### Search Result Formatting

```python
# Customize how search results are presented to Claude
search_context = "\n\n## Web Search Results\n"
for result in search_results:
    search_context += f"**{result['title']}**\n"
    search_context += f"Source: {result['url']}\n"
    search_context += f"{result['description']}\n\n"
```

### Multi-Source Search

```python
# Combine multiple search sources
async def enhanced_search(query: str):
    brave_results = await brave_search(query)
    # Add other sources if needed
    return brave_results
```

---

## ?? Summary

### What You Get

? **Automatic web search** when users ask about current events  
? **Brave Search API** integration (privacy-focused)  
? **Smart detection** of time-sensitive queries  
? **Source citations** in Claude's responses  
? **Graceful fallback** if search is unavailable  
? **Zero code changes** required (backward compatible)

### Quick Setup

1. Get Brave API key: https://brave.com/search/api/
2. Add to `.env`: `BRAVE_SEARCH_API_KEY=xxx`
3. Restart your app
4. Done! Search now works automatically

### Try It Out

```python
# Just add the API key and try:
response = await claude.generate_response(
    "What's the latest news on AI technology today?"
)
# Claude will search the web and cite sources! ??
```

---

## ?? Resources

- **Brave Search API**: https://brave.com/search/api/
- **API Documentation**: https://api.search.brave.com/app/documentation/web-search/get-started
- **Pricing**: https://brave.com/search/api/#pricing
- **Support**: https://community.brave.com/

---

**Questions?** Check the code in `utils/claude_client.py` or reach out for help!
