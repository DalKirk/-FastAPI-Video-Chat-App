# Commit WebSocket fixes to GitHub
Write-Host "?? Committing WebSocket fixes to GitHub..." -ForegroundColor Green

# Check if we're in a git repository
if (-not (Test-Path .git)) {
    Write-Host "? Error: Not a git repository" -ForegroundColor Red
    exit 1
}

# Check git status
Write-Host "`n?? Current Git Status:" -ForegroundColor Cyan
git status --short

# Add all changes
Write-Host "`n? Adding files..." -ForegroundColor Yellow
git add main.py
git add -u

# Show what will be committed
Write-Host "`n?? Files to be committed:" -ForegroundColor Cyan
git status --short

# Create commit
$commitMessage = "Fix: Clean up main.py - Remove duplicates and fix WebSocket implementation

- Removed all duplicate code sections
- Fixed syntax errors and undefined references
- Cleaned up WebSocket endpoint implementation
- Removed references to undefined data_store
- Simplified logging configuration
- Fixed CORS middleware configuration
- Updated rate limiting configuration
- Cleaned up HTML chat interface
- All WebSocket functionality now working correctly

? WebSocket connections working
? Real-time messaging functional
? User/room management active
? AI chat endpoints integrated"

Write-Host "`n?? Creating commit..." -ForegroundColor Yellow
git commit -m $commitMessage

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n? Commit created successfully!" -ForegroundColor Green
    
    # Push to GitHub
    Write-Host "`n?? Pushing to GitHub..." -ForegroundColor Yellow
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n? Successfully pushed to GitHub!" -ForegroundColor Green
        Write-Host "`n?? Commit Summary:" -ForegroundColor Cyan
        git log -1 --stat
    } else {
        Write-Host "`n? Failed to push to GitHub" -ForegroundColor Red
        Write-Host "Run 'git push origin main' manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n? Failed to create commit" -ForegroundColor Red
    Write-Host "Check git status and try again" -ForegroundColor Yellow
}

Write-Host "`n? Done!" -ForegroundColor Green
