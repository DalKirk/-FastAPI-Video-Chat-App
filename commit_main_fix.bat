@echo off
echo ========================================
echo Committing WebSocket Fixes to GitHub
echo ========================================
echo.

REM Check if we're in a git repository
if not exist .git (
    echo ERROR: Not a git repository
    exit /b 1
)

echo Current Git Status:
git status --short
echo.

echo Adding main.py to staging...
git add main.py
echo.

echo Files staged for commit:
git status --short
echo.

echo Creating commit...
git commit -m "Fix: Clean up main.py and fix WebSocket implementation

- Removed all duplicate code sections and syntax errors
- Fixed WebSocket endpoint with proper error handling
- Cleaned up imports and removed unused dependencies
- Simplified logging configuration
- Fixed CORS middleware configuration
- Updated rate limiting configuration
- Cleaned up HTML chat interface
- Removed all references to undefined data_store
- All WebSocket functionality now working correctly

Changes:
- WebSocket connections working
- Real-time messaging functional
- User/room management active
- AI chat endpoints integrated
- Clean, production-ready code"

if errorlevel 1 (
    echo ERROR: Failed to create commit
    echo Please check git status and try again
    pause
    exit /b 1
)

echo.
echo Commit created successfully!
echo.

echo Pushing to GitHub...
git push origin main

if errorlevel 1 (
    echo ERROR: Failed to push to GitHub
    echo You may need to pull first or resolve conflicts
    echo Run: git pull origin main
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS! Pushed to GitHub
echo ========================================
echo.

echo Commit Summary:
git log -1 --stat
echo.

echo Done!
pause
