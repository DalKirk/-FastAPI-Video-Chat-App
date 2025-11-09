@echo off
echo ====================================
echo Restoring main.py and Fixing 405
echo ====================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Step 1: Reset main.py to working version...
git fetch origin
git checkout origin/main -- main.py

echo.
echo Step 2: Check if file was restored...
findstr /C:"@app.get(\"/\")" main.py
if errorlevel 1 (
    echo ERROR: Root endpoint not found in main.py!
    echo File may be corrupted. Please restore manually.
    pause
    exit /b 1
)

echo.
echo Step 3: File looks good! Committing and pushing...
git add main.py
git commit -m "fix: restore main.py with all endpoints and proper OPTIONS handler order"
git push origin main

echo.
echo ====================================
echo Done! Railway will redeploy in ~2 mins
echo The 405 errors should be fixed
echo ====================================
pause
