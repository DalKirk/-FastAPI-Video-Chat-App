@echo off
REM Simple Git Commit Script - No PowerShell
echo ====================================
echo Git Commit and Push Script
echo ====================================
echo.

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

REM Clean up problematic files
echo Cleaning up problematic files...
del /s /q *.pyc 2>nul
del /s /q *.log 2>nul
del /s /q *.lock 2>nul
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

echo.
echo Current Git Status:
git status

echo.
echo Adding all files...
git add -A

echo.
echo Committing changes...
git commit -m "Update FastAPI Video Chat Application - main.py improvements"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ====================================
echo Done! Check output above for any errors.
echo ====================================
pause
