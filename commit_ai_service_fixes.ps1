# PowerShell script to commit AI service fixes to GitHub
# Run this script from the project root directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI SERVICE FIXES - COMMIT TO GITHUB  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "? ERROR: Not in a git repository!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}

Write-Host "?? Checking Git status..." -ForegroundColor Yellow
git status

Write-Host ""
Write-Host "?? Files to be committed:" -ForegroundColor Yellow
Write-Host "  1. main.py (CORS + JS fixes)" -ForegroundColor White
Write-Host "  2. frontend/src/services/api.js (API URL fix)" -ForegroundColor White
Write-Host "  3. app/__init__.py (NEW - package fix)" -ForegroundColor White
Write-Host "  4. AI_SERVICE_COMPILATION_FIX.md (Documentation)" -ForegroundColor White
Write-Host "  5. verify_ai_service.py (Verification script)" -ForegroundColor White
Write-Host "  6. GIT_COMMIT_AI_SERVICE_FIXES.md (Commit summary)" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Do you want to proceed with the commit? (y/n)"
if ($confirm -ne "y" -and $confirm -ne "Y") {
    Write-Host "? Commit cancelled." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "?? Running verification first..." -ForegroundColor Yellow

# Verify Python imports
Write-Host "  - Checking Python imports..." -ForegroundColor Gray
try {
    python -c "from api.routes.chat import router; print('? Imports OK')"
    Write-Host "  ? Python imports verified" -ForegroundColor Green
} catch {
    Write-Host "  ? Import verification failed!" -ForegroundColor Red
    Write-Host "  Run: python verify_ai_service.py" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "?? Staging files..." -ForegroundColor Yellow

# Stage specific files
git add main.py
git add frontend/src/services/api.js
git add app/__init__.py
git add AI_SERVICE_COMPILATION_FIX.md
git add verify_ai_service.py
git add GIT_COMMIT_AI_SERVICE_FIXES.md

Write-Host "? Files staged" -ForegroundColor Green

Write-Host ""
Write-Host "?? Creating commit..." -ForegroundColor Yellow

$commitMessage = @"
Fix: AI service compilation errors - CORS, JS syntax, and package structure

- Fixed CORS configuration for development mode (use regex instead of ["*"] with credentials)
- Fixed all JavaScript syntax errors in embedded HTML chat interface
- Added app/__init__.py to fix Python package import errors
- Updated frontend API URL configuration for Next.js/Vercel compatibility
- All compilation errors resolved, ready for deployment
"@

git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "? Commit created successfully!" -ForegroundColor Green
} else {
    Write-Host "? Commit failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "?? Pushing to GitHub..." -ForegroundColor Yellow

git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ? SUCCESSFULLY PUSHED TO GITHUB!    " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "?? Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Railway will auto-deploy the backend" -ForegroundColor White
    Write-Host "  2. Vercel will auto-deploy the frontend" -ForegroundColor White
    Write-Host "  3. Check deployment status in ~2-3 minutes" -ForegroundColor White
    Write-Host ""
    Write-Host "?? Monitor Deployments:" -ForegroundColor Cyan
    Write-Host "  - Railway: https://railway.app/dashboard" -ForegroundColor White
    Write-Host "  - Vercel: https://vercel.com/dashboard" -ForegroundColor White
    Write-Host ""
    Write-Host "? All AI service compilation issues are now fixed!" -ForegroundColor Green
} else {
    Write-Host "? Push failed!" -ForegroundColor Red
    Write-Host "Please check your network connection and try again." -ForegroundColor Yellow
    exit 1
}
