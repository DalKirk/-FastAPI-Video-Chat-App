# Add Legacy Health Check Redirect to main.py

After line 242 in main.py (`app.include_router(chat_router)`), add this code:

```python
# Legacy redirects for old health check endpoints
from fastapi.responses import RedirectResponse as RedirectResp

@app.get("/ai/health")
async def legacy_ai_health_redirect():
    """Redirect legacy /ai/health to new endpoint"""
    return RedirectResp(url="/api/v1/chat/health", status_code=301)
```

This will redirect Railway's health checks from `/ai/health` to `/api/v1/chat/health`.

Save the file and push to GitHub.
