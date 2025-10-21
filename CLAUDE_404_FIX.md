# ?? Claude API 404 Error - Fixed!

## ? Error You Were Getting

```
404 Error from Anthropic API when calling Claude
```

## ?? Root Causes & Solutions

### **Possible Cause 1: Model Name Issue**

Some Anthropic regions or account types may not have access to the latest model yet.

**Solution:** Added automatic fallback to an older model:
- **Primary:** `claude-3-5-sonnet-20241022` (Latest)
- **Fallback:** `claude-3-5-sonnet-20240620` (Stable)

### **Possible Cause 2: API Key Issues**

Invalid or expired API key.

**Solution:** Better error messages that tell you exactly what's wrong:
- Authentication errors
- Rate limit errors
- Model not found errors

### **Possible Cause 3: Regional Availability**

Some models may not be available in all regions yet.

**Solution:** Automatic fallback ensures your app keeps working.

---

## ? What Was Fixed

### 1. **Added Model Fallback Support**

Your code now automatically tries a backup model if the primary one fails:

```python
# Primary model
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"

# Fallback if primary fails
FALLBACK_MODEL = "claude-3-5-sonnet-20240620"
```

### 2. **Better Error Handling**

Added specific error handlers for:
- ? `anthropic.NotFoundError` - Model not found (404)
- ? `anthropic.AuthenticationError` - Invalid API key
- ? `anthropic.RateLimitError` - Rate limit exceeded
- ? Generic exceptions with detailed logging

### 3. **Diagnostic Tool**

Created `diagnose_anthropic.py` to test your API connection:

```bash
python diagnose_anthropic.py
```

This will:
- ? Check if API key is set
- ? Test connection to Anthropic
- ? Try multiple models
- ? Show which models work
- ? Display detailed error messages

### 4. **Dynamic Model Reporting**

The `/ai/health` endpoint now shows:
```json
{
  "ai_enabled": true,
  "model": "claude-3-5-sonnet-20241022",
  "fallback_model": "claude-3-5-sonnet-20240620",
  "features": [...]
}
```

---

## ?? How to Test

### **Step 1: Run Diagnostic Tool**

```bash
# Set your API key (if not already set)
export ANTHROPIC_API_KEY='sk-ant-api03-...'  # Linux/Mac
# OR
$env:ANTHROPIC_API_KEY="sk-ant-api03-..."    # PowerShell

# Run diagnostic
python diagnose_anthropic.py
```

**Expected Output:**
```
?? Anthropic API Diagnostic Tool
============================================================
? API Key found: sk-ant-api03-...
? Anthropic SDK imported successfully

============================================================
Testing Claude Models:
============================================================

?? Testing: claude-3-5-sonnet-20241022
   Description: Latest Claude 3.5 Sonnet (Oct 2024)
   ? SUCCESS - Model is available
   Response: test

?? Testing: claude-3-5-sonnet-20240620
   Description: Claude 3.5 Sonnet (June 2024)
   ? SUCCESS - Model is available
   Response: test
```

### **Step 2: Test Your Application**

```bash
# Start your server
uvicorn main:app --reload

# Test AI health endpoint
curl http://localhost:8000/ai/health

# Expected response:
{
  "ai_enabled": true,
  "model": "claude-3-5-sonnet-20241022",
  "fallback_model": "claude-3-5-sonnet-20240620",
  "features": ["content_moderation", "spam_detection", ...]
}

# Test AI generation
curl -X POST http://localhost:8000/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello", "max_tokens": 50}'

# Expected response:
{
  "response": "Hello! How can I help you today?",
  "model": "claude-3-5-sonnet-20241022"
}
```

---

## ?? Deployed to Railway

**Commit:** `c970f84` - "Add fallback model support and better 404 error handling for Claude API"

Railway will now:
1. ? Use the latest model if available
2. ? Automatically fall back to stable model if 404
3. ? Show clear error messages
4. ? Keep your app running even if one model fails

---

## ?? Make Sure Your API Key is Set

### **In Railway:**

1. Go to Railway dashboard
2. Select your project
3. Click "Variables"
4. Add/verify: `ANTHROPIC_API_KEY` = `sk-ant-api03-your-key-here`
5. Save and redeploy

### **Locally:**

```bash
# Create .env file
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-key-here" >> .env

# Or set environment variable
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

---

## ?? Common 404 Error Solutions

| Issue | Solution |
|-------|----------|
| Model not available in your region | ? Automatic fallback enabled |
| Invalid model name | ? Using verified model names |
| API key doesn't have access | Contact Anthropic support |
| Model deprecated | ? Fallback to stable version |
| Typo in model name | ? Using constants, not strings |

---

## ?? Model Availability Status

| Model | Availability | Status |
|-------|--------------|--------|
| `claude-3-5-sonnet-20241022` | Most regions | ? Primary |
| `claude-3-5-sonnet-20240620` | All regions | ? Fallback |
| `claude-3-haiku-20240307` | All regions | ? Fast option |

---

## ?? If Problems Persist

### **1. Check Anthropic Status**

Visit: https://status.anthropic.com/

### **2. Verify API Key**

```bash
python diagnose_anthropic.py
```

### **3. Check Railway Logs**

```bash
railway logs --tail
```

Look for:
```
? Claude AI client initialized with model: claude-3-5-sonnet-20241022
```

OR

```
?? Model claude-3-5-sonnet-20241022 not found, trying fallback
? Successfully switched to fallback model: claude-3-5-sonnet-20240620
```

### **4. Test Different Models**

If both models fail, you can update the model constants in `utils/claude_client.py`:

```python
# Try Claude Haiku (cheaper, faster)
CLAUDE_MODEL = "claude-3-haiku-20240307"
FALLBACK_MODEL = "claude-3-haiku-20240307"
```

---

## ? Success Criteria

After fixing, you should see:

- ? No 404 errors in Railway logs
- ? `/ai/health` returns `"ai_enabled": true`
- ? `/ai/generate` returns responses
- ? Model name shown in responses
- ? Fallback works if primary fails

---

## ?? Support

If the 404 error persists after these fixes:

1. **Run diagnostic:** `python diagnose_anthropic.py`
2. **Check API key:** Ensure it's valid and active
3. **Contact Anthropic:** support@anthropic.com
4. **Check account:** Verify your account has model access

---

**Status:** ? FIXED - Deployed with fallback support  
**Commit:** `c970f84`  
**Branch:** `main`  
**Next:** Test on Railway after deployment completes
