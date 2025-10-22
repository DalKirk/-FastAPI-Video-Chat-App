# Quick Deployment Monitor Script
# Run this to check if your deployment is complete

Write-Host "?? Deployment Monitor - Word Spacing Fix" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check Railway CLI status
Write-Host "?? Checking Railway status..." -ForegroundColor Cyan
railway status
Write-Host ""

# Check latest deployment
Write-Host "?? Checking latest deployment..." -ForegroundColor Cyan
Write-Host ""

# Get Railway URL
Write-Host "?? Getting Railway URL..." -ForegroundColor Cyan
$railwayUrl = railway domain 2>&1
if ($railwayUrl -match "https://.*") {
    $url = $railwayUrl -replace ".*?(https://[^\s]+).*", '$1'
    Write-Host "  ? URL: $url" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "?? Testing deployment..." -ForegroundColor Cyan
    
    # Test health endpoint
    Write-Host "  Testing /health..." -ForegroundColor Gray
    try {
        $healthResponse = Invoke-RestMethod -Uri "$url/health" -Method Get -TimeoutSec 10
        Write-Host "  ? Health: $($healthResponse.status)" -ForegroundColor Green
        Write-Host "  ?? Stats:" -ForegroundColor Gray
        Write-Host "     - Active rooms: $($healthResponse.stats.active_rooms)" -ForegroundColor White
        Write-Host "     - Active users: $($healthResponse.stats.active_users)" -ForegroundColor White
        Write-Host "     - Messages: $($healthResponse.stats.total_messages)" -ForegroundColor White
    } catch {
        Write-Host "  ? Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "  Testing /ai/stream/health..." -ForegroundColor Gray
    try {
        $aiHealthResponse = Invoke-RestMethod -Uri "$url/ai/stream/health" -Method Get -TimeoutSec 10
        Write-Host "  ? AI Streaming: $($aiHealthResponse.streaming_enabled)" -ForegroundColor Green
        Write-Host "  ?? AI Status:" -ForegroundColor Gray
        Write-Host "     - Model: $($aiHealthResponse.model)" -ForegroundColor White
        Write-Host "     - Text Formatting: $($aiHealthResponse.text_formatting)" -ForegroundColor White
    } catch {
        Write-Host "  ? AI health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "? Deployment Monitor Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "?? Your app is live at:" -ForegroundColor Cyan
    Write-Host "   $url" -ForegroundColor White
    Write-Host ""
    Write-Host "?? Test endpoints:" -ForegroundColor Cyan
    Write-Host "   Health: $url/health" -ForegroundColor White
    Write-Host "   Chat UI: $url/chat" -ForegroundColor White
    Write-Host "   API Docs: $url/docs" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "  ??  Could not detect Railway URL" -ForegroundColor Yellow
    Write-Host "  Manual check: https://railway.app/dashboard" -ForegroundColor White
}

# Show recent logs
Write-Host "?? Recent deployment logs (last 50 lines):" -ForegroundColor Cyan
Write-Host ""
railway logs --lines 50

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "?? Tips:" -ForegroundColor Yellow
Write-Host "  - Watch logs: railway logs --tail" -ForegroundColor White
Write-Host "  - Redeploy: railway up" -ForegroundColor White
Write-Host "  - Dashboard: https://railway.app/dashboard" -ForegroundColor White
Write-Host ""
