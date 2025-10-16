# Railway Deployment Script for Windows PowerShell

Write-Host "🚀 Starting Railway Deployment..." -ForegroundColor Green

# Check if Railway CLI is installed
if (Get-Command "railway" -ErrorAction SilentlyContinue) {
    Write-Host "✅ Railway CLI found" -ForegroundColor Green
} else {
    Write-Host "❌ Railway CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

# Check login status
Write-Host "🔐 Checking Railway login..." -ForegroundColor Cyan
$loginResult = railway whoami 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Already logged in to Railway" -ForegroundColor Green
} else {
    Write-Host "🔑 Please login to Railway..." -ForegroundColor Yellow
    railway login
}

# Initialize project
Write-Host "📝 Initializing Railway project..." -ForegroundColor Cyan
railway init

# Deploy the application
Write-Host "🚀 Deploying to Railway..." -ForegroundColor Cyan
railway up

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "📊 Check your deployment at: https://railway.app/dashboard" -ForegroundColor Cyan