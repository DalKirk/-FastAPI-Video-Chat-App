# ?? Claude AI Integration Guide

## ? Installation Complete!

The Anthropic Claude SDK has been installed and integrated into your FastAPI Video Chat application.

---

## ?? What Was Installed

1. **Anthropic SDK** (`anthropic>=0.71.0`)
2. **Claude Client Utility** (`utils/claude_client.py`)
3. **AI Endpoints** (`utils/ai_endpoints.py`)
4. **Environment Template** (updated `.env.example`)

---

## ?? Setup Your API Key

### Step 1: Get Your Claude API Key

1. Visit: https://console.anthropic.com/
2. Sign in or create an account
3. Go to **API Keys** section
4. Click **Create Key**
5. Copy your API key

### Step 2: Add to Your Local Environment

Create or update your `.env` file:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

### Step 3: Add to Railway (Production)

```bash
# Using Railway CLI
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Or via Railway Dashboard:
# 1. Go to your project
# 2. Settings ? Variables
# 3. Add: ANTHROPIC_API_KEY = sk-ant-api03-your-key-here
```

---

## ?? Quick Start

### Option 1: Use AI Endpoints in Your App

Add to your `main.py`:

```python
from utils.ai_endpoints import ai_router

# Add AI router
app.include_router(ai_router)
```

Then your app will have these endpoints:
- `POST /ai/generate` - Generate AI responses
- `POST /ai/moderate` - Content moderation
- `POST /ai/detect-spam` - Spam detection
- `POST /ai/summarize` - Conversation summarization
- `POST /ai/suggest-reply` - Smart reply suggestions
- `GET /ai/health` - Check AI feature status

### Option 2: Use Claude Client Directly

```python
from utils.claude_client import get_claude_client

# In your endpoint
claude = get_claude_client()

# Generate response
response = claude.generate_response("Hello, how are you?")

# Moderate content
moderation = claude.moderate_content("This is a test message")
if not moderation["is_safe"]:
    # Block the message
    pass

# Detect spam
is_spam = claude.detect_spam("Buy now! Click here!")
```

---

## ?? Use Cases

### 1. **Content Moderation**

Automatically moderate chat messages:

```python
@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, user_id: str):
    while True:
        data = await websocket.receive_text()
        message_data = json.loads(data)
        
        # Moderate content with Claude
        claude = get_claude_client()
        moderation = claude.moderate_content(message_data["content"])
        
        if not moderation["is_safe"]:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": f"Message blocked: {moderation['reason']}"
            }))
            continue
        
        # ... rest of your code
```

### 2. **Spam Detection**

```python
# In your create message endpoint
claude = get_claude_client()
if claude.detect_spam(message_content):
    raise HTTPException(status_code=400, detail="Spam detected")
```

### 3. **Smart Replies**

```python
# Suggest replies to users
recent_messages = get_recent_messages(room_id, limit=5)
context = "\n".join([f"{m.username}: {m.content}" for m in recent_messages])

claude = get_claude_client()
suggestion = claude.suggest_reply(context, new_message)
```

### 4. **Conversation Summaries**

```python
# Summarize long conversations
messages = get_room_messages(room_id, limit=50)
claude = get_claude_client()
summary = claude.summarize_conversation(messages)
```

---

## ?? API Examples

### Test Content Moderation

```bash
curl -X POST http://localhost:8000/ai/moderate \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello everyone! Welcome to the chat!"}'
```

**Response:**
```json
{
  "is_safe": true,
  "reason": "No violations detected",
  "confidence": 0.95
}
```

### Generate AI Response

```bash
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a fun icebreaker question for a video chat",
    "max_tokens": 100,
    "temperature": 0.8
  }'
```

### Check AI Health

```bash
curl http://localhost:8000/ai/health
```

**Response:**
```json
{
  "ai_enabled": true,
  "model": "claude-3-5-sonnet-20241022",
  "features": [
    "content_moderation",
    "spam_detection",
    "conversation_summary",
    "smart_replies",
    "ai_generation"
  ]
}
```

---

## ?? Pricing

Claude API pricing (as of 2024):

| Model | Input | Output |
|-------|-------|--------|
| Claude 3.5 Sonnet | $3/MTok | $15/MTok |
| Claude 3 Haiku | $0.25/MTok | $1.25/MTok |

**Recommendations:**
- Use **Sonnet** for content moderation (high accuracy)
- Use **Haiku** for simple tasks (cost-effective)
- Set `max_tokens` limits to control costs
- Cache frequently used prompts

---

## ?? Security Best Practices

1. **Never commit API keys** to Git
2. **Use environment variables** for all secrets
3. **Add rate limiting** to AI endpoints:
   ```python
   from middleware.rate_limit import RateLimitMiddleware
   
   # Stricter limits for AI endpoints
   app.add_middleware(
       RateLimitMiddleware,
       requests_limit=10,  # 10 requests per minute
       time_window=60,
       exclude_paths={"/health"}
   )
   ```
4. **Monitor API usage** in Anthropic Console
5. **Set spending limits** in your Anthropic account

---

## ?? Testing

Test the integration locally:

```python
# test_claude.py
from utils.claude_client import ClaudeClient
import os

# Set your API key
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-api03-..."

# Test basic functionality
claude = ClaudeClient()

# Test generation
response = claude.generate_response("Hello!")
print(f"Response: {response}")

# Test moderation
moderation = claude.moderate_content("This is a test message")
print(f"Moderation: {moderation}")

# Test spam detection
is_spam = claude.detect_spam("Buy now! Click here for free stuff!")
print(f"Is Spam: {is_spam}")
```

Run it:
```bash
python test_claude.py
```

---

## ?? Deployment Checklist

- [ ] API key added to `.env` locally
- [ ] API key added to Railway environment variables
- [ ] `requirements.txt` updated (? done)
- [ ] AI endpoints added to `main.py` (optional)
- [ ] Rate limiting configured for AI endpoints
- [ ] Spending limits set in Anthropic Console
- [ ] Test all AI features locally
- [ ] Deploy and verify on production

---

## ?? Monitoring

Monitor your Claude API usage:

1. **Anthropic Console**: https://console.anthropic.com/
2. **Usage Dashboard**: View requests, tokens, and costs
3. **Set Alerts**: Get notified of high usage
4. **Review Logs**: Check for errors or abuse

---

## ?? Troubleshooting

### "Claude AI is not configured"

**Solution:** Add `ANTHROPIC_API_KEY` to your environment variables.

### "Rate limit exceeded"

**Solution:** You've hit Anthropic's rate limits. Wait or upgrade your plan.

### "Invalid API key"

**Solution:** 
1. Check your API key is correct
2. Ensure no extra spaces
3. Verify key hasn't been revoked

### AI responses are slow

**Solution:**
1. Use Claude Haiku for faster responses
2. Reduce `max_tokens`
3. Add caching for common queries

---

## ?? You're All Set!

Your FastAPI Video Chat app now has:
- ? Claude AI SDK installed
- ? Content moderation utilities
- ? Spam detection
- ? Smart reply suggestions
- ? Conversation summarization
- ? Ready-to-use API endpoints

**Next Steps:**
1. Add your API key to `.env`
2. Test locally with `python test_claude.py`
3. Add AI endpoints to `main.py`
4. Deploy to Railway
5. Monitor usage in Anthropic Console

---

**Questions?** Check the docs:
- Anthropic API Docs: https://docs.anthropic.com/
- Claude Models: https://docs.anthropic.com/claude/docs/models-overview
- Pricing: https://www.anthropic.com/pricing
