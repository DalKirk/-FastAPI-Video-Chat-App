@echo off
echo ================================================
echo  Committing WebSocket Fix to GitHub
echo ================================================
echo.

REM Stage only the essential files
echo [1/4] Staging files...
git add main.py
git add static\chat.html

echo.
echo [2/4] Committing...
git commit -m "fix: WebSocket room connection error handling"

echo.
echo [3/4] Pushing to GitHub...
git push origin main

echo.
echo [4/4] Done!
echo.
echo ================================================
echo  Check Railway in 2-3 minutes for auto-deploy
echo ================================================
echo.
pause
