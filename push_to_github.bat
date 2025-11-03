@echo off
REM Simple batch script to commit and push changes to GitHub
echo ====================================
echo Pushing changes to GitHub
echo ====================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Checking for corrupted files...
REM Clean up any corrupted files with invalid names
for /f "delims=" %%F in ('git ls-files 2^>nul') do (
    echo %%F | findstr /C:"} finally {" >nul
    if not errorlevel 1 (
        echo Removing corrupted file: %%F
        git rm --cached "%%F" >nul 2>&1
    )
)

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
