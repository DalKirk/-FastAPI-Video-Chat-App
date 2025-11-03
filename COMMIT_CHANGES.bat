@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Safe, robust commit + push (Windows CMD)
cd /d "%~dp0"

echo === Status/Remote ===
git status
if errorlevel 1 goto :fail

git remote -v

REM Detect branch (fallback to main)
for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
if "%BRANCH%"=="" set BRANCH=main

echo === Stage All ===
git add -A
if errorlevel 1 goto :fail


echo === Staged Files ===
git diff --cached --name-only

REM Use multiple -m flags instead of a multi-line quoted message

echo === Commit ===
git commit -m "Add Brave search support and conversation history features" ^
            -m "Features added:" ^
            -m "- Brave Search API integration in Claude client" ^
            -m "- Conversation history tracking with conversation_id support" ^
            -m "- Web search detection based on keywords (today, now, current, latest, etc.)" ^
            -m "- Search results injection into Claude context" ^
            -m "- Streaming endpoints enhanced with search capabilities" ^
            -m "- enable_search parameter for all endpoints" ^
            -m "- Updated health checks to show search status" ^
            -m "- Perfect markdown formatting preservation" ^
            -m "- Conversation management endpoints (clear, get history, get count)" ^
            -m "" ^
            -m "Technical improvements:" ^
            -m "- Removed _restore_newlines function that was corrupting output" ^
            -m "- Added search metadata to streaming completion events" ^
            -m "- Enhanced request/response models with conversation_id fields" ^
            -m "- Integrated httpx for async web requests" ^
            -m "- Fallback model support with automatic switching" ^
            -m "- Comprehensive error handling and logging"
if errorlevel 1 (
  echo (Possibly nothing to commit) Continuing...
)

echo === Pull --rebase origin/%BRANCH% ===
git pull --rebase origin %BRANCH%


echo === Push origin/%BRANCH% ===
git push -u origin %BRANCH%
if errorlevel 1 goto :fail

echo SUCCESS
endlocal
exit /b 0

:fail
echo FAILED. Check the messages above.
endlocal
exit /b 1