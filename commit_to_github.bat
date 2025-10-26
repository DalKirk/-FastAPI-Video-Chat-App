@echo off
echo ========================================
echo   AI SERVICE FIXES - COMMIT TO GITHUB
echo ========================================
echo.

echo Staging files...
git add main.py
git add frontend/src/services/api.js
git add app/__init__.py
git add AI_SERVICE_COMPILATION_FIX.md
git add verify_ai_service.py
git add GIT_COMMIT_AI_SERVICE_FIXES.md
git add MANUAL_COMMIT_GUIDE.md
git add commit_ai_service_fixes.ps1

echo.
echo Creating commit...
git commit -m "Fix: AI service compilation errors - CORS, JS syntax, and package structure" -m "- Fixed CORS configuration for development mode (use regex instead of [\"*\"] with credentials)" -m "- Fixed all JavaScript syntax errors in embedded HTML chat interface" -m "- Added app/__init__.py to fix Python package import errors" -m "- Updated frontend API URL configuration for Next.js/Vercel compatibility" -m "- All compilation errors resolved, ready for deployment"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   DONE! Check Railway for deployment
echo ========================================
echo.
pause
