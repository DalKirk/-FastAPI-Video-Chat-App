@echo off
REM Ultimate Git Commit Script - Handles OneDrive Issues
echo ==========================================
echo Git Commit Script (OneDrive Safe)
echo ==========================================
echo.

REM Navigate to project directory
cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo Step 1: Cleaning temporary files...
if exist __pycache__ rd /s /q __pycache__ 2>nul
del /q *.pyc 2>nul
del /q *.log 2>nul
del /q *.lock 2>nul
echo    Done.
echo.

echo Step 2: Checking Git status...
git status -s
echo.

echo Step 3: Staging files...
git add main.py
git add .gitignore
git add requirements.txt
git add README.md
echo    Files staged.
echo.

echo Step 4: Creating commit...
git commit -m "Update FastAPI Video Chat Application v2.0.0 - Enhanced features and fixes"
echo.

echo Step 5: Pushing to GitHub...
git push origin main
echo.

if %errorlevel% equ 0 (
    echo ==========================================
    echo SUCCESS! Changes pushed to GitHub
    echo ==========================================
) else (
    echo ==========================================
    echo ERROR! Push failed. Error code: %errorlevel%
    echo ==========================================
    echo.
    echo Possible solutions:
    echo 1. Check your internet connection
    echo 2. Verify GitHub credentials
    echo 3. Try: git push origin main --force
    echo.
)

pause
