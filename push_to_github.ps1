# PowerShell script to push changes to GitHub
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Pushing changes to GitHub" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

$repoPath = "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"
Set-Location $repoPath

Write-Host "`nStaging all changes..." -ForegroundColor Yellow
git add -A

Write-Host "`nCreating commit..." -ForegroundColor Yellow
git commit -m "feat(ai): add web-search and conversation features" -m "- Add Claude web search integration" -m "- Add conversation history support" -m "- Update AI endpoints with streaming"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Commit created successfully!" -ForegroundColor Green
} elseif (git status --porcelain) {
    Write-Host "Commit failed!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "No changes to commit" -ForegroundColor Yellow
}

Write-Host "`nPulling latest changes..." -ForegroundColor Yellow
git pull --rebase origin main

Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n====================================" -ForegroundColor Green
    Write-Host "SUCCESS! Changes pushed to GitHub" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
} else {
    Write-Host "`n====================================" -ForegroundColor Red
    Write-Host "FAILED! Check errors above" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
    exit 1
}
