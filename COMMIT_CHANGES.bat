@echo off
echo Adding files to Git...
git add utils/claude_client.py
git add utils/streaming_ai_endpoints.py
git add app/models/chat_models.py
git add services/ai_service.py
git add api/routes/chat.py

echo Committing changes...
git commit -m "Add Brave search support and conversation history features

Features added:
- Brave Search API integration in Claude client
- Conversation history tracking with conversation_id support
- Web search detection based on keywords (today, now, current, latest, etc.)
- Search results injection into Claude context
- Streaming endpoints enhanced with search capabilities
- enable_search parameter for all endpoints
- Updated health checks to show search status
- Perfect markdown formatting preservation
- Conversation management endpoints (clear, get history, get count)

Technical improvements:
- Removed _restore_newlines function that was corrupting output
- Added search metadata to streaming completion events
- Enhanced request/response models with conversation_id fields
- Integrated httpx for async web requests
- Fallback model support with automatic switching
- Comprehensive error handling and logging"

echo Pushing to GitHub...
git push origin main

echo Done! Check GitHub to verify the commit.
pause