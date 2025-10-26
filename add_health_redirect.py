#!/usr/bin/env python3
"""Add legacy health redirect to main.py"""

with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with app.include_router(chat_router)
idx = next(i for i, line in enumerate(lines) if 'app.include_router(chat_router)' in line)

# Insert redirect after it
redirect_code = """
# Legacy redirect for health check monitors
from fastapi.responses import RedirectResponse as RResp

@app.get("/ai/health")
async def legacy_ai_health():
    \"\"\"Redirect old /ai/health to new endpoint\"\"\"
    return RResp(url="/api/v1/chat/health", status_code=301)

"""

lines.insert(idx + 1, redirect_code)

with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("? Added legacy health check redirect to main.py")
