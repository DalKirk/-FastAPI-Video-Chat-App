# Push changes to GitHub
Write-Host "Adding files to Git..." -ForegroundColor Cyan

# Add the rate limit middleware
git add middleware/rate_limit.py

# Check status
Write-Host "`nChecking Git status..." -ForegroundColor Cyan
git status

# Commit changes
Write-Host "`nCommitting changes..." -ForegroundColor Cyan
git commit -m "Add rate limiting middleware for API protection"

# Push to GitHub
Write-Host "`nPushing to GitHub..." -ForegroundColor Cyan
git push origin main

Write-Host "`nChanges pushed successfully!" -ForegroundColor Green
Write-Host "View your repository at: https://github.com/DalKirk/-FastAPI-Video-Chat-App" -ForegroundColor Yellow
