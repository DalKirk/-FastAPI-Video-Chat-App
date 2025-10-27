#!/usr/bin/env pwsh
# Quick Start Script - Test WebSocket Fix
# Run this after making the fixes

Write-Host "?? WebSocket Chat Fix - Quick Start" -ForegroundColor Green
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""

# Check if server is already running
Write-Host "?? Checking if server is already running..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "? Server is already running!" -ForegroundColor Green
    $serverRunning = $true
} catch {
    Write-Host "??  Server is not running" -ForegroundColor Yellow
    $serverRunning = $false
}

if (-not $serverRunning) {
    Write-Host ""
    Write-Host "?? Starting server..." -ForegroundColor Cyan
    Write-Host "   Command: uvicorn main:app --reload --port 8000" -ForegroundColor Gray
    Write-Host ""
    Write-Host "??  Server will start in a new window" -ForegroundColor Yellow
    Write-Host "   Keep that window open while testing!" -ForegroundColor Yellow
    Write-Host ""
    
    # Start server in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn main:app --reload --port 8000"
    
    # Wait for server to start
    Write-Host "? Waiting for server to start..." -ForegroundColor Cyan
    $maxAttempts = 20
    $attempt = 0
    $serverReady = $false
    
    while ($attempt -lt $maxAttempts -and -not $serverReady) {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
            $serverReady = $true
        } catch {
            $attempt++
            Write-Host "." -NoNewline -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    
    if ($serverReady) {
        Write-Host "? Server started successfully!" -ForegroundColor Green
    } else {
        Write-Host "? Server failed to start in time" -ForegroundColor Red
        Write-Host "   Please start it manually: python -m uvicorn main:app --reload" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "?? Running Diagnostics..." -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""

# Run diagnostic script
python diagnose_chat_rooms.py

Write-Host ""
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "?? Opening Browser..." -ForegroundColor Cyan
Write-Host "=" -ForegroundColor Green -NoNewline
Write-Host "=" * 50 -ForegroundColor Green
Write-Host ""

# Open browser
Write-Host "?? Opening http://localhost:8000/chat in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:8000/chat"

Write-Host ""
Write-Host "? Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "?? Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Browser should open automatically" -ForegroundColor White
Write-Host "   2. Create a user (enter username, click 'Create User')" -ForegroundColor White
Write-Host "   3. Create a room (enter room name, click 'Create Room')" -ForegroundColor White
Write-Host "   4. Click 'Load Rooms' to see available rooms" -ForegroundColor White
Write-Host "   5. Click 'Join' to connect to the room" -ForegroundColor White
Write-Host "   6. Start chatting!" -ForegroundColor White
Write-Host ""
Write-Host "?? Tips:" -ForegroundColor Yellow
Write-Host "   - Press F12 in browser to see console logs" -ForegroundColor Gray
Write-Host "   - Server is running in a separate window" -ForegroundColor Gray
Write-Host "   - Check server logs if you see errors" -ForegroundColor Gray
Write-Host ""
Write-Host "?? Documentation:" -ForegroundColor Cyan
Write-Host "   - COMPLETE_FIX_README.md - Complete guide" -ForegroundColor Gray
Write-Host "   - WEBSOCKET_FIX_SUMMARY.md - Technical details" -ForegroundColor Gray
Write-Host "   - WEBSOCKET_CONNECTION_FIXES.md - Troubleshooting" -ForegroundColor Gray
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
