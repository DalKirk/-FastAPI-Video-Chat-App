@echo off
echo ====================================
echo Restoring main.py from Good Commit
echo ====================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Restoring main.py from commit 04309d3...
echo (This was the last working version before corruption)

git checkout 04309d3 -- main.py

echo.
echo Verifying restoration...
findstr /C:"def root():" main.py
if errorlevel 1 (
    echo ERROR: Restoration failed!
    echo Trying alternative commit 65da3df...
    git checkout 65da3df -- main.py
    findstr /C:"def root():" main.py
    if errorlevel 1 (
        echo CRITICAL: Cannot restore from any commit!
        echo Please manually download main.py from GitHub
        pause
        exit /b 1
    )
)

echo.
echo SUCCESS: File restored with all endpoints!
echo.

echo Adding and committing...
git add main.py
git commit -m "fix: restore main.py from working commit - fixes 405 errors"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ====================================
echo SUCCESS! Railway will redeploy now
echo Wait ~2 minutes then test:
echo   curl https://web-production-3ba7e.up.railway.app/health
echo ====================================
pause
