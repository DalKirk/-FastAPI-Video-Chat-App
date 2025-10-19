# Setup Vercel Environment Variables
# This script adds the Railway backend URLs to your Vercel frontend

Write-Host "?? Setting up Vercel Environment Variables..." -ForegroundColor Green
Write-Host ""

# Configuration
$FRONTEND_DIR = "C:\Users\g-kd\OneDrive\Desktop\video-chat-frontend"
$API_URL = "https://web-production-3ba7e.up.railway.app"
$WS_URL = "wss://web-production-3ba7e.up.railway.app"

# Check if Vercel CLI is installed
Write-Host "? Checking Vercel CLI..." -ForegroundColor Cyan
$vercelVersion = vercel --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? Vercel CLI found: $vercelVersion" -ForegroundColor Green
} else {
    Write-Host "  ? Vercel CLI not found. Please install it:" -ForegroundColor Red
    Write-Host "  npm install -g vercel" -ForegroundColor Yellow
    exit 1
}

# Navigate to frontend directory
Write-Host ""
Write-Host "? Navigating to frontend directory..." -ForegroundColor Cyan
if (Test-Path $FRONTEND_DIR) {
    Set-Location $FRONTEND_DIR
    Write-Host "  ? Found: $FRONTEND_DIR" -ForegroundColor Green
} else {
    Write-Host "  ? Frontend directory not found: $FRONTEND_DIR" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "????????????????????????????????????????????????????????" -ForegroundColor Yellow
Write-Host "  MANUAL STEPS REQUIRED" -ForegroundColor Yellow
Write-Host "????????????????????????????????????????????????????????" -ForegroundColor Yellow
Write-Host ""
Write-Host "The following commands need to be run interactively:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Login to Vercel (if not already):" -ForegroundColor White
Write-Host "   vercel login" -ForegroundColor Green
Write-Host ""
Write-Host "2. Link to your project (if not already):" -ForegroundColor White
Write-Host "   vercel link" -ForegroundColor Green
Write-Host ""
Write-Host "3. Add API URL environment variable:" -ForegroundColor White
Write-Host "   vercel env add NEXT_PUBLIC_API_URL production" -ForegroundColor Green
Write-Host "   When prompted, paste: $API_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Add WebSocket URL environment variable:" -ForegroundColor White
Write-Host "   vercel env add NEXT_PUBLIC_WS_URL production" -ForegroundColor Green
Write-Host "   When prompted, paste: $WS_URL" -ForegroundColor Yellow
Write-Host ""
Write-Host "5. Redeploy your project:" -ForegroundColor White
Write-Host "   vercel --prod" -ForegroundColor Green
Write-Host ""
Write-Host "????????????????????????????????????????????????????????" -ForegroundColor Yellow
Write-Host ""
Write-Host "?? Quick Copy-Paste Values:" -ForegroundColor Cyan
Write-Host ""
Write-Host "API_URL:  $API_URL" -ForegroundColor White
Write-Host "WS_URL:   $WS_URL" -ForegroundColor White
Write-Host ""
Write-Host "????????????????????????????????????????????????????????" -ForegroundColor Yellow
Write-Host ""
Write-Host "?? TIP: Or add them via Vercel Dashboard:" -ForegroundColor Cyan
Write-Host "   1. Go to https://vercel.com/dashboard" -ForegroundColor White
Write-Host "   2. Select your project" -ForegroundColor White
Write-Host "   3. Settings ? Environment Variables" -ForegroundColor White
Write-Host "   4. Add the two variables above" -ForegroundColor White
Write-Host "   5. Redeploy" -ForegroundColor White
Write-Host ""
