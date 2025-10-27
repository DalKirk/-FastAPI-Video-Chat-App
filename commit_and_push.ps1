# Simple Git Commit and Push Script
# Commits the WebSocket fixes and pushes to GitHub

Write-Host "?? Committing WebSocket Fixes to GitHub" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
Write-Host ""

# Check git status first
Write-Host "?? Current Git Status:" -ForegroundColor Cyan
git status --short
Write-Host ""

# Add all the fixed files
Write-Host "?? Adding files to staging..." -ForegroundColor Cyan
git add main.py
git add static/chat.html
git add diagnose_chat_rooms.py
git add quick_start_test.ps1
git add ALL_CHANGES_SUMMARY.md
git add COMPLETE_FIX_README.md
git add START_HERE.md
git add WEBSOCKET_CONNECTION_FIXES.md
git add WEBSOCKET_FIX_SUMMARY.md

Write-Host "? Files staged" -ForegroundColor Green
Write-Host ""

# Show what's staged
Write-Host "?? Files to be committed:" -ForegroundColor Cyan
git status --short
Write-Host ""

# Commit with a simple message
Write-Host "?? Committing changes..." -ForegroundColor Cyan
git commit -m "fix: WebSocket room connection - handle join errors properly"

if ($LASTEXITCODE -eq 0) {
    Write-Host "? Commit successful!" -ForegroundColor Green
    Write-Host ""
    
    # Push to GitHub
    Write-Host "?? Pushing to GitHub..." -ForegroundColor Cyan
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host "? Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host ""
        Write-Host "?? Your changes are now live on:" -ForegroundColor Cyan
        Write-Host "   https://github.com/DalKirk/-FastAPI-Video-Chat-App" -ForegroundColor White
        Write-Host ""
        Write-Host "?? Railway will auto-deploy in 2-3 minutes" -ForegroundColor Yellow
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "? Push failed!" -ForegroundColor Red
        Write-Host "Try manually: git push origin main" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "? Commit failed!" -ForegroundColor Red
    Write-Host "Check the error above" -ForegroundColor Yellow
    exit 1
}

Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
