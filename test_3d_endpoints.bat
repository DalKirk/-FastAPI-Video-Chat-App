@echo off
echo ====================================
echo Testing 3D Model API Endpoints
echo ====================================

echo.
echo 1. Testing Health Endpoint...
curl -X GET https://web-production-3ba7e.up.railway.app/api/v1/3d/health

echo.
echo.
echo 2. Testing Generate Endpoint (POST)...
curl -X POST https://web-production-3ba7e.up.railway.app/api/v1/3d/generate ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"A red cube\", \"style\": \"realistic\", \"complexity\": \"simple\"}"

echo.
echo.
echo 3. Testing OPTIONS (CORS preflight)...
curl -X OPTIONS https://web-production-3ba7e.up.railway.app/api/v1/3d/generate ^
  -H "Origin: https://next-js-14-front-end-for-chat-plast-kappa.vercel.app" ^
  -H "Access-Control-Request-Method: POST" ^
  -v

echo.
echo ====================================
echo Test Complete
echo ====================================
pause
