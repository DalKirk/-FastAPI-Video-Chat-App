# ?? Web Search Integration - Quick Start

## ? 5-Minute Setup

### Step 1: Get API Keys (2 min)

**Anthropic Claude** (Required)
- Visit: https://console.anthropic.com/
- Create account ? API Keys ? Create Key
- Copy: `sk-ant-api03-...`

**Brave Search** (Optional, but recommended)
- Visit: https://brave.com/search/api/
- Sign up ? Create API Key
- Copy: `BSA...`

### Step 2: Configure Environment (1 min)

Add to your `.env` file:

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Optional (enables web search)
BRAVE_SEARCH_API_KEY=BSAyour-key-here
```

### Step 3: Test Locally (1 min)

```bash
# Run tests
python test_ai_endpoints_complete.py

# Start server
python main.py
```

### Step 4: Deploy (1 min)

```bash
# Railway
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-...
railway variables set BRAVE_SEARCH_API_KEY=BSA...

# Git push
git add .
git commit -m "Add web search integration"
git push
```

---

## ? That's It!

Your app now has:
- ? AI responses with Claude
- ? Automatic web search
- ? Conversation history
- ? Source citations

---

## ?? Test It

```bash
# Check status
curl http://localhost:8000/ai/health

# Test search
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the latest AI developments?", "enable_search": true}'
```

---

## ?? Frontend Usage

```javascript
// Enable search (default)
const response = await fetch('/api/ai/generate', {
  method: 'POST',
  body: JSON.stringify({
    prompt: "What's happening in tech today?",
    enable_search: true  // Auto-searches
  })
});

// Disable search
const response = await fetch('/api/ai/generate', {
  method: 'POST',
  body: JSON.stringify({
    prompt: "Explain Python",
    enable_search: false  // No search needed
  })
});
```

---

## ?? Automatic Search Triggers

These queries automatically search:
- "What's the weather **today**?"
- "**Latest** news on AI"
- "What happened **this week**?"
- "**Current** stock prices"

No special setup needed!

---

## ?? Free Tier Limits

- **Claude**: $5 free credit
- **Brave Search**: 1,000 queries/month free

---

## ?? Need More Help?

- **Full Guide**: `docs/WEB_SEARCH_GUIDE.md`
- **API Docs**: `COMPLETE_INTEGRATION_FINAL.md`
- **Test Suite**: `test_ai_endpoints_complete.py`

---

## ?? You're Ready!

**Setup Time:** 5 minutes  
**Difficulty:** Easy  
**Cost:** Free to start  

**Just add your API keys and deploy! ??**
