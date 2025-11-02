# ? Web Search Integration - Setup Checklist

## ?? Pre-Deployment Checklist

### 1. API Keys Configuration
- [ ] Obtained Brave Search API key from https://brave.com/search/api/
- [ ] Added `BRAVE_SEARCH_API_KEY` to local `.env` file
- [ ] Verified `ANTHROPIC_API_KEY` is set in `.env`
- [ ] Tested locally with both API keys

### 2. Local Testing
- [ ] Run `python -m py_compile utils/claude_client.py` ?
- [ ] Run `python -m py_compile services/ai_service.py` ?
- [ ] Run `python -m py_compile utils/ai_endpoints.py` ?
- [ ] Run `python test_web_search.py`
- [ ] Verify search detection works
- [ ] Verify conversation history works
- [ ] Check logs for "Web search enabled" message

### 3. Code Review
- [ ] Review changes in `utils/claude_client.py`
- [ ] Review changes in `services/ai_service.py`
- [ ] Review changes in `utils/ai_endpoints.py`
- [ ] Verify all async methods use `await`
- [ ] Check error handling is in place

### 4. Documentation
- [ ] Read `docs/WEB_SEARCH_GUIDE.md`
- [ ] Read `IMPLEMENTATION_SUMMARY.md`
- [ ] Read `WEB_SEARCH_QUICK_REF.md`
- [ ] Understand search trigger keywords
- [ ] Know how to disable search if needed

---

## ?? Deployment Checklist

### 5. Production Environment
- [ ] Add `BRAVE_SEARCH_API_KEY` to Railway/production env
- [ ] Verify `ANTHROPIC_API_KEY` exists in production
- [ ] Check `httpx>=0.28.0` is in `requirements.txt` ?
- [ ] Verify `anthropic>=0.19.0` is in `requirements.txt` ?

### 6. Deploy to Production
- [ ] Commit all changes to Git
  ```bash
  git add .
  git commit -m "Add web search integration with Brave API"
  git push origin main
  ```
- [ ] Deploy to Railway/production platform
- [ ] Wait for deployment to complete
- [ ] Check deployment logs for errors

### 7. Production Testing
- [ ] Test basic AI response (no search)
- [ ] Test search-triggered query ("latest news")
- [ ] Test conversation history
- [ ] Verify logging is working
- [ ] Check API usage in Brave dashboard

### 8. Monitoring Setup
- [ ] Enable logging in production
- [ ] Set up Brave API usage alerts
- [ ] Configure rate limiting if needed
- [ ] Monitor initial usage patterns
- [ ] Set spending alerts in Brave dashboard

---

## ?? Quick Tests

### Test 1: API Keys
```bash
# Check local environment
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('ANTHROPIC_API_KEY:', 'SET' if os.getenv('ANTHROPIC_API_KEY') else 'NOT SET'); print('BRAVE_SEARCH_API_KEY:', 'SET' if os.getenv('BRAVE_SEARCH_API_KEY') else 'NOT SET')"
```

### Test 2: Syntax Check
```bash
python -m py_compile utils/claude_client.py
python -m py_compile services/ai_service.py
python -m py_compile utils/ai_endpoints.py
python -m py_compile test_web_search.py
```

### Test 3: Full Test Suite
```bash
python test_web_search.py
```

### Test 4: Quick Search Test
```bash
python -c "
from utils.claude_client import get_claude_client
import asyncio

async def test():
    claude = get_claude_client()
    print('AI Enabled:', claude.is_enabled)
    print('Search Enabled:', claude.is_search_enabled)
    if claude.is_enabled:
        response = await claude.generate_response('Hello')
        print('Response length:', len(response))

asyncio.run(test())
"
```

---

## ?? Feature Verification

### ? Core Features
- [ ] Claude AI responding correctly
- [ ] Web search detection working
- [ ] Search results being used
- [ ] Source citations present
- [ ] Conversation history maintained
- [ ] Graceful fallback without search

### ? Search Triggers
Test these queries trigger search:
- [ ] "What's the weather today?"
- [ ] "Latest news on AI"
- [ ] "What happened this week?"
- [ ] "Current stock price"
- [ ] "Recent developments in..."

Test these DON'T trigger search:
- [ ] "Explain Python"
- [ ] "How to code"
- [ ] "What is quantum physics?"

### ? Error Handling
- [ ] Works without Brave API key (search disabled)
- [ ] Handles search API timeouts
- [ ] Handles rate limits gracefully
- [ ] Handles network errors
- [ ] Logs errors appropriately

---

## ?? Performance Checks

### Before Deployment
- [ ] Response time < 5 seconds (with search)
- [ ] Response time < 2 seconds (without search)
- [ ] Memory usage normal
- [ ] No async/await warnings
- [ ] No syntax errors

### After Deployment
- [ ] Production endpoints responding
- [ ] Search working in production
- [ ] Logs showing search activity
- [ ] API usage within limits
- [ ] No error spikes in logs

---

## ?? Security Verification

### API Key Security
- [ ] Keys not in Git repository
- [ ] Keys in `.env` file (gitignored)
- [ ] Keys in production env vars
- [ ] No hardcoded keys in code
- [ ] `.env.example` has placeholders only

### Rate Limiting
- [ ] Rate limiting configured
- [ ] Limits appropriate for usage
- [ ] Monitoring rate limit hits
- [ ] Alerts set up for abuse

### Input Validation
- [ ] User inputs validated
- [ ] Query length limits set
- [ ] SQL injection protected
- [ ] XSS protection in place

---

## ?? Monitoring Checklist

### Week 1
- [ ] Monitor daily API usage
- [ ] Check error rates
- [ ] Review search patterns
- [ ] Verify no rate limit hits
- [ ] Check response times

### Week 2-4
- [ ] Analyze search query patterns
- [ ] Optimize search triggers if needed
- [ ] Review API costs
- [ ] Adjust rate limits if needed
- [ ] Consider caching strategy

### Ongoing
- [ ] Monthly API usage review
- [ ] Cost analysis
- [ ] Performance optimization
- [ ] Feature enhancement planning

---

## ?? Rollback Plan

### If Issues Occur

1. **Quick Rollback**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Disable Search Only**
   ```bash
   # Remove BRAVE_SEARCH_API_KEY from environment
   railway variables unset BRAVE_SEARCH_API_KEY
   ```

3. **Emergency Disable**
   ```python
   # In claude_client.py, set:
   enable_search=False  # Default parameter
   ```

---

## ?? Documentation Checklist

### Available Documentation
- [x] `docs/WEB_SEARCH_GUIDE.md` - Complete guide
- [x] `IMPLEMENTATION_SUMMARY.md` - Technical details
- [x] `WEB_SEARCH_QUICK_REF.md` - Quick reference
- [x] `test_web_search.py` - Test suite
- [x] Code comments in `utils/claude_client.py`

### Team Knowledge Transfer
- [ ] Share documentation with team
- [ ] Demo the feature
- [ ] Explain search trigger keywords
- [ ] Show how to disable search
- [ ] Review monitoring dashboard

---

## ? Sign-Off Checklist

### Developer Sign-Off
- [ ] All code reviewed
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Local testing successful
- [ ] Ready for deployment

### QA Sign-Off
- [ ] Feature tested locally
- [ ] Edge cases covered
- [ ] Error handling verified
- [ ] Performance acceptable
- [ ] Ready for production

### Deployment Sign-Off
- [ ] Production env configured
- [ ] Deployment successful
- [ ] Production tests passing
- [ ] Monitoring active
- [ ] Feature live

---

## ?? Success Criteria

The integration is successful when:

? **Functionality**
- Claude AI responds correctly
- Search automatically triggers on appropriate queries
- Results include source citations
- Conversation history works
- No breaking changes to existing features

? **Performance**
- Response time < 5 seconds with search
- No memory leaks
- Stable under load
- Graceful error handling

? **Monitoring**
- Logs show search activity
- API usage tracked
- No critical errors
- Within rate limits and budget

? **Documentation**
- All docs complete
- Team trained
- Runbooks created
- Examples working

---

## ?? Support Contacts

### Internal
- Developer: Check code in `utils/claude_client.py`
- Documentation: See `docs/WEB_SEARCH_GUIDE.md`
- Tests: Run `python test_web_search.py`

### External
- Brave Search Support: https://community.brave.com/
- Brave API Docs: https://api.search.brave.com/app/documentation
- Anthropic Support: https://support.anthropic.com/

---

## ?? Post-Deployment Tasks

### Immediate (Day 1)
- [ ] Monitor error logs
- [ ] Check API usage
- [ ] Verify search working
- [ ] Test main user flows
- [ ] Address any issues

### Short-term (Week 1)
- [ ] Analyze usage patterns
- [ ] Review performance metrics
- [ ] Collect user feedback
- [ ] Optimize if needed
- [ ] Update documentation

### Long-term (Month 1)
- [ ] Cost analysis
- [ ] Feature enhancement planning
- [ ] Caching implementation
- [ ] Advanced monitoring setup
- [ ] Team training sessions

---

**Date Completed:** _____________

**Deployed By:** _____________

**Verified By:** _____________

**Status:** ? Ready to Deploy | ? In Progress | ? Deployed | ? Verified

---

**Notes:**
_____________________________________________________
_____________________________________________________
_____________________________________________________
