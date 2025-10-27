@echo off
REM Simple Git Commit and Push Script
REM Commits the WebSocket fixes and pushes to GitHub

echo.
echo ========================================
echo   Committing WebSocket Fixes to GitHub
echo ========================================
echo.

REM Add files
echo Adding files...
git add main.py
git add static\chat.html
git add diagnose_chat_rooms.py
git add quick_start_test.ps1
git add ALL_CHANGES_SUMMARY.md
git add COMPLETE_FIX_README.md
git add START_HERE.md
git add WEBSOCKET_CONNECTION_FIXES.md
git add WEBSOCKET_FIX_SUMMARY.md

echo.
echo Files staged. Current status:
git status --short

echo.
echo Committing...
git commit -m "fix: WebSocket room connection - handle join errors properly"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Commit failed!
    pause
    exit /b 1
)

echo.
echo Commit successful! Pushing to GitHub...
git push origin main

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Push failed!
    echo Try manually: git push origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Successfully pushed to GitHub!
echo ========================================
echo.
echo Railway will auto-deploy in 2-3 minutes
echo.
pause
