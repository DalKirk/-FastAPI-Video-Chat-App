# Quick Redeploy Script for FastAPI Video Chat
# Redeploys both backend (Railway) and frontend (Vercel)

Write-Host "?? FastAPI Video Chat - Quick Redeploy Script" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""

# Configuration
$BACKEND_DIR = "C:\Users\g-kd\OneDrive\Desktop\My_FastAPI_Python"
$FRONTEND_DIR = "C:\Users\g-kd\OneDrive\Desktop\video-chat-frontend"

# Check if Railway CLI is installed
Write-Host "?? Checking Railway CLI..." -ForegroundColor Cyan
$railwayVersion = railway --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? Railway CLI found: $railwayVersion" -ForegroundColor Green
} else {
    Write-Host "  ??  Railway CLI not found" -ForegroundColor Yellow
}

# Check if Vercel CLI is installed
Write-Host "?? Checking Vercel CLI..." -ForegroundColor Cyan
$vercelVersion = vercel --version 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ? Vercel CLI found: $vercelVersion" -ForegroundColor Green
} else {
    Write-Host "  ??  Vercel CLI not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "What would you like to redeploy?" -ForegroundColor Yellow
Write-Host "  1. Backend only (Railway)" -ForegroundColor White
Write-Host "  2. Frontend only (Vercel)" -ForegroundColor White
Write-Host "  3. Both Backend and Frontend" -ForegroundColor White
Write-Host "  4. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "?? Redeploying Backend to Railway..." -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path $BACKEND_DIR) {
            Set-Location $BACKEND_DIR
            
            Write-Host "?? Current directory: $BACKEND_DIR" -ForegroundColor Gray
            Write-Host ""
            
            # Check for uncommitted changes
            $gitStatus = git status --porcelain
            if ($gitStatus) {
                Write-Host "??  You have uncommitted changes:" -ForegroundColor Yellow
                git status --short
                Write-Host ""
                $commit = Read-Host "Commit changes before deploying? (y/n)"
                if ($commit -eq "y") {
                    git add .
                    $commitMsg = Read-Host "Enter commit message"
                    git commit -m "$commitMsg"
                    git push origin main
                    Write-Host "? Changes committed and pushed" -ForegroundColor Green
                }
            }
            
            Write-Host ""
            Write-Host "?? Deploying to Railway..." -ForegroundColor Cyan
            railway up
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "? Backend deployed successfully!" -ForegroundColor Green
                Write-Host ""
                Write-Host "?? Test your backend:" -ForegroundColor Cyan
                Write-Host "   https://web-production-3ba7e.up.railway.app/health" -ForegroundColor White
            } else {
                Write-Host ""
                Write-Host "? Deployment failed. Check the error above." -ForegroundColor Red
            }
        } else {
            Write-Host "? Backend directory not found: $BACKEND_DIR" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "?? Redeploying Frontend to Vercel..." -ForegroundColor Cyan
        Write-Host ""
        
        if (Test-Path $FRONTEND_DIR) {
            Set-Location $FRONTEND_DIR
            
            Write-Host "?? Current directory: $FRONTEND_DIR" -ForegroundColor Gray
            Write-Host ""
            
            # Check for uncommitted changes
            $gitStatus = git status --porcelain
            if ($gitStatus) {
                Write-Host "??  You have uncommitted changes:" -ForegroundColor Yellow
                git status --short
                Write-Host ""
                $commit = Read-Host "Commit changes before deploying? (y/n)"
                if ($commit -eq "y") {
                    git add .
                    $commitMsg = Read-Host "Enter commit message"
                    git commit -m "$commitMsg"
                    git push origin main
                    Write-Host "? Changes committed and pushed (Vercel will auto-deploy)" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "? Vercel is automatically deploying..." -ForegroundColor Cyan
                    Write-Host "   Check status at: https://vercel.com/dashboard" -ForegroundColor White
                }
            } else {
                Write-Host "??  No uncommitted changes. Triggering redeploy..." -ForegroundColor Cyan
                Write-Host ""
                
                $method = Read-Host "Use Vercel CLI or make empty commit? (cli/commit)"
                if ($method -eq "cli") {
                    vercel --prod
                } else {
                    git commit --allow-empty -m "chore: trigger redeploy"
                    git push origin main
                    Write-Host "? Redeployment triggered via Git push" -ForegroundColor Green
                }
            }
            
            Write-Host ""
            Write-Host "? Frontend redeployment initiated!" -ForegroundColor Green
            Write-Host ""
            Write-Host "?? Check deployment status:" -ForegroundColor Cyan
            Write-Host "   https://vercel.com/dashboard" -ForegroundColor White
        } else {
            Write-Host "? Frontend directory not found: $FRONTEND_DIR" -ForegroundColor Red
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "?? Redeploying Both Backend and Frontend..." -ForegroundColor Cyan
        Write-Host ""
        
        # Deploy Backend
        Write-Host "????????????????????????????????????????" -ForegroundColor Yellow
        Write-Host "  BACKEND (Railway)" -ForegroundColor Yellow
        Write-Host "????????????????????????????????????????" -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path $BACKEND_DIR) {
            Set-Location $BACKEND_DIR
            
            $gitStatus = git status --porcelain
            if ($gitStatus) {
                Write-Host "??  Backend has uncommitted changes" -ForegroundColor Yellow
                $commit = Read-Host "Commit backend changes? (y/n)"
                if ($commit -eq "y") {
                    git add .
                    $commitMsg = Read-Host "Enter commit message"
                    git commit -m "$commitMsg"
                    git push origin main
                }
            }
            
            Write-Host "?? Deploying backend..." -ForegroundColor Cyan
            railway up
            Write-Host ""
        }
        
        # Deploy Frontend
        Write-Host "????????????????????????????????????????" -ForegroundColor Yellow
        Write-Host "  FRONTEND (Vercel)" -ForegroundColor Yellow
        Write-Host "????????????????????????????????????????" -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path $FRONTEND_DIR) {
            Set-Location $FRONTEND_DIR
            
            $gitStatus = git status --porcelain
            if ($gitStatus) {
                Write-Host "??  Frontend has uncommitted changes" -ForegroundColor Yellow
                $commit = Read-Host "Commit frontend changes? (y/n)"
                if ($commit -eq "y") {
                    git add .
                    $commitMsg = Read-Host "Enter commit message"
                    git commit -m "$commitMsg"
                    git push origin main
                }
            } else {
                git commit --allow-empty -m "chore: trigger redeploy"
                git push origin main
            }
            Write-Host ""
        }
        
        Write-Host "? Both deployments initiated!" -ForegroundColor Green
        Write-Host ""
        Write-Host "?? Backend:  https://web-production-3ba7e.up.railway.app/health" -ForegroundColor Cyan
        Write-Host "?? Frontend: https://next-js-14-front-end-for-chat-plast.vercel.app" -ForegroundColor Cyan
    }
    
    "4" {
        Write-Host ""
        Write-Host "?? Goodbye!" -ForegroundColor Cyan
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "? Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "????????????????????????????????????????" -ForegroundColor Green
Write-Host "  Deployment Complete!" -ForegroundColor Green
Write-Host "????????????????????????????????????????" -ForegroundColor Green
Write-Host ""
Write-Host "?? Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Wait 1-2 minutes for deployment to complete" -ForegroundColor White
Write-Host "  2. Check health: curl https://web-production-3ba7e.up.railway.app/health" -ForegroundColor White
Write-Host "  3. Test frontend: https://next-js-14-front-end-for-chat-plast.vercel.app" -ForegroundColor White
Write-Host ""
