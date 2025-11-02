# ?? Web Search Quick Reference

## ?? Quick Setup

```bash
# 1. Get API key from https://brave.com/search/api/
# 2. Add to .env
BRAVE_SEARCH_API_KEY=BSAxxxxxxxxxxxxxxxxxx

# 3. Restart app
python main.py

# 4. Test
python test_web_search.py
```

---

## ?? Code Examples

### Basic Usage

```python
from utils.claude_client import get_claude_client

claude = get_claude_client()

# Automatic search (default)
response = await claude.generate_response(
    "What's the latest news on AI today?"
)

# Disable search
response = await claude.generate_response(
    "Explain quantum physics",
    enable_search=False
)

# Check if search is enabled
if claude.is_search_enabled:
    print("Search is active!")
```

### FastAPI Endpoint

```python
@app.post("/chat")
async def chat(message: str, user_id: str):
    claude = get_claude_client()
    response = await claude.generate_response(
        message,
        conversation_id=user_id
    )
    return {"response": response}
```

### WebSocket

```python
@app.websocket("/ws/{user_id}")
async def ws_chat(websocket: WebSocket, user_id: str):
    await websocket.accept()
    claude = get_claude_client()
    
    while True:
        msg = await websocket.receive_text()
        reply = await claude.generate_response(
            msg,
            conversation_id=user_id
        )
        await websocket.send_text(reply)
```

---

## ?? Search Triggers

Queries with these keywords **automatically** search:

? **Temporal**: today, now, current, latest, recent  
? **News**: news, what's happening, update on  
? **Time**: this week, this month, this year  
? **Years**: 2024, 2025

**Examples:**
- "What's the weather today?" ? Searches ?
- "Latest AI developments" ? Searches ?
- "Explain Python" ? No search ?

---

## ?? Configuration

### Change Search Result Count

In `utils/claude_client.py`:
```python
# Default: 5 results
search_results = await self._search_web(query, count=5)

# More results (max 20)
search_results = await self._search_web(query, count=10)
```

### Add Custom Keywords

```python
# In _detect_search_need():
current_indicators = [
    "today", "now", "current", # existing
    "breaking", "trending"     # add yours
]
```

---

## ?? Status Check

```python
claude = get_claude_client()
info = claude.get_model_info()

print(f"""
AI Enabled: {info['is_enabled']}
Search Enabled: {info['is_search_enabled']}
Model: {info['active_model']}
Conversations: {info['active_conversations']}
""")
```

---

## ?? Troubleshooting

| Issue | Solution |
|-------|----------|
| Search not working | Check `BRAVE_SEARCH_API_KEY` in .env |
| Rate limit | Upgrade Brave plan or add caching |
| No sources cited | Verify search triggered with logs |
| Timeout errors | Check network, increase timeout |

**Check logs for:**
```
INFO - Detected search need for: [query]
INFO - Web search returned 5 results
```

---

## ?? Pricing

| Plan | Queries/Month | Cost |
|------|---------------|------|
| Free | 1,000 | $0 |
| Basic | 10,000 | $5 |
| Pro | 100,000 | $50 |

**Get free API key**: https://brave.com/search/api/

---

## ? Testing

```bash
# Full test suite
python test_web_search.py

# Quick test
python -c "
from utils.claude_client import get_claude_client
import asyncio

async def test():
    claude = get_claude_client()
    print('Search enabled:', claude.is_search_enabled)
    response = await claude.generate_response('Latest AI news')
    print('Response:', response[:200])

asyncio.run(test())
"
```

---

## ?? Documentation

- **Full Guide**: `docs/WEB_SEARCH_GUIDE.md`
- **Implementation Details**: `WEB_SEARCH_IMPLEMENTATION.md`
- **Test Script**: `test_web_search.py`
- **Source Code**: `utils/claude_client.py`

---

## ?? Features

? Automatic search detection  
? Brave Search integration  
? Source citations  
? Conversation history  
? Graceful fallback  
? Zero breaking changes  
? Production ready  

**Setup time: 5 minutes** ??
