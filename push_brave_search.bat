@echo off
echo ====================================
echo Adding Brave Search to Streaming
echo ====================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Staging changes...
git add utils/streaming_ai_endpoints.py

echo.
echo Committing...
git commit -m "feat: add Brave Search integration to streaming endpoints" -m "- Add Brave Search API integration" -m "- Inject web search results into system prompt" -m "- Enable real-time web data in responses" -m "- Add enable_search flag to request models" -m "- Update health endpoint to show search status"

echo.
echo Pulling latest...
git pull --rebase origin main

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ====================================
echo Done! Railway will deploy in ~2 mins
echo Make sure BRAVE_SEARCH_API_KEY is set in Railway
echo ====================================
pause
