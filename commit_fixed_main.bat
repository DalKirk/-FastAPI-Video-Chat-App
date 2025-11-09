@echo off
echo ===============================================
echo Fixing Duplicates and Committing main.py
echo ===============================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Step 1: Checking for errors...
python -c "import ast; ast.parse(open('main.py').read())" 2>nul
if errorlevel 1 (
    echo ERROR: main.py has syntax errors!
    echo Please fix manually before committing.
    pause
    exit /b 1
)

echo.
echo Step 2: File looks syntactically correct!
echo.
echo Manual fixes needed:
echo   1. Remove lines 228-230 (duplicate router registrations)
echo   2. Remove lines 284-295 (duplicate ai_health and ai_proxy)
echo   3. Remove line 557 (duplicate static mount)
echo.
echo OR use this quick fix:
echo   - Open main.py in your IDE
echo   - Delete lines 228-230, 284-295, and 557
echo   - Save the file
echo.

pause

echo.
echo Step 3: Adding to git...
git add main.py

echo.
echo Step 4: Committing...
git commit -m "fix: restore all endpoints and remove duplicates"

echo.
echo Step 5: Pushing to GitHub...
git push origin main

echo.
echo ===============================================
echo Done! Railway will redeploy in ~2 mins
echo All 405 errors should be fixed now!
echo ===============================================
pause
