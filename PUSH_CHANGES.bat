@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Robust Git push script for Windows (non-interactive)
echo ========================================
echo Git Push Script (robust)
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"
echo Working directory: %CD%

REM Step 1: Show status and remotes
echo --- git status ---
git status

echo --- remotes ---
git remote -v

REM Step 2: Stage ALL changes (new/modified/deleted)
echo --- staging changes ---
git add -A
if errorlevel 1 (
    echo ERROR: git add failed
    goto :end_fail
)

REM Step 3: Show staged files
echo --- staged files ---
git diff --cached --name-only

REM Step 4: Create commit (continue if nothing to commit)
set COMMIT_MSG=Update: AI service and related changes^&^&Ensure markdown handling and search flag wiring^&^&Push script robustness: stage all, non-interactive, rebase before push
for /f "delims=" %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i
if "%BRANCH%"=="" set BRANCH=main

echo --- creating commit on branch %BRANCH% ---
git commit -m "Update: AI service and related changes" -m "Ensure markdown handling and search flag wiring" -m "Push script robustness: stage all, non-interactive, rebase before push"
if errorlevel 1 (
    echo NOTE: Commit may have failed (possibly no changes to commit). Continuing...
)

REM Step 5: Rebase pull to avoid non-fast-forward

echo --- pulling latest with rebase from origin/%BRANCH% ---
git pull --rebase origin %BRANCH%
if errorlevel 1 (
    echo WARNING: Pull --rebase encountered issues. You may need to resolve conflicts.
)

REM Step 6: Push to GitHub

echo --- pushing to origin/%BRANCH% ---
git push -u origin %BRANCH%
if errorlevel 1 (
    echo ERROR: Git push failed
    echo Possible reasons:
    echo  - Authentication required
    echo  - Network issues / VPN
    echo  - Branch protection rules
    echo  - Remote changes need to be pulled first
    goto :end_fail
)

echo.
echo ========================================
echo SUCCESS! Changes pushed to GitHub

echo ========================================
endlocal
exit /b 0

:end_fail
echo.
echo ========================================
echo FAILED to push changes

echo ========================================
endlocal
exit /b 1
