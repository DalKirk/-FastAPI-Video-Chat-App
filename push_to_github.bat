@echo off
REM Simple batch script to push changes to GitHub
echo ====================================
echo Pushing changes to GitHub
echo ====================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Staging all changes...
git add -A

echo.
echo Creating commit...
git commit -m "feat(ai): add web-search and conversation features" -m "- Add Claude web search integration" -m "- Add conversation history support" -m "- Update AI endpoints with streaming"

echo.
echo Pulling latest changes...
git pull --rebase origin main

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ====================================
echo Done! Check output above for status
echo ====================================
pause
