@echo off
echo ========================================
echo Git Repository Diagnostic
echo ========================================
echo.

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo [1] Current Directory:
cd
echo.

echo [2] Git Remote:
git remote -v
echo.

echo [3] Current Branch:
git branch
echo.

echo [4] Git Status (Short):
git status -s
echo.

echo [5] Last Commit:
git log -1 --oneline
echo.

echo [6] Checking for large files (over 50MB):
git ls-files -z | xargs -0 du -h 2>nul | findstr /R "[0-9][0-9]M"
echo.

echo [7] Modified Files:
git diff --name-only
echo.

echo [8] Staged Files:
git diff --cached --name-only
echo.

echo [9] Untracked Files:
git ls-files --others --exclude-standard
echo.

echo ========================================
echo Diagnostic Complete
echo ========================================
pause
