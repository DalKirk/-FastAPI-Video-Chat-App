@echo off
echo ====================================
echo Adding 3D Model Generation Feature
echo ====================================

cd /d "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"

echo.
echo Staging files...
git add api/routes/model_3d.py
git add requirements.txt
git add main.py
git add static/models/

echo.
echo Committing...
git commit -m "feat: add 3D model generation with Claude AI" -m "- Add /api/v1/3d/generate endpoint" -m "- Use Claude to generate 3D model specifications" -m "- Create procedural GLB models with trimesh" -m "- Add model management endpoints (list, get, delete)" -m "- Serve models via /static/models/" -m "- Support multiple styles and complexity levels"

echo.
echo Pulling latest...
git pull --rebase origin main

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ====================================
echo Done! Railway will deploy in ~3 mins
echo Install dependencies: pip install trimesh numpy Pillow pygltflib
echo ====================================
pause
