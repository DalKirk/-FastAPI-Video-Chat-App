# Fix stuck Git state and push changes
param(
  [string]$Branch = "main",
  [string]$Remote = "origin"
)

$ErrorActionPreference = "Stop"

function Info($msg){ Write-Host $msg -ForegroundColor Cyan }
function Warn($msg){ Write-Host $msg -ForegroundColor Yellow }
function Good($msg){ Write-Host $msg -ForegroundColor Green }

Info "Closing possible locks..."
$lock = Join-Path -Path (Resolve-Path .) -ChildPath ".git/index.lock"
if (Test-Path $lock) { Remove-Item $lock -Force }

Info "Killing stray git processes..."
Get-Process git -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Get-Process "git-remote-https" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

Info "Cleaning odd untracked files..."
# Best-effort removal of previously reported weird files
$weird = @(
  "t * findstr claude * finally *",
  "tatus * finally *"
)
foreach ($pattern in $weird) {
  Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like $pattern } | ForEach-Object {
    Warn "Removing: $($_.FullName)"
    Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
  }
}

Info "Running git gc..."
git gc

Info "Checking status..."
git status

Info "Adding changes..."
git add -A

Info "Committing..."
try {
  git commit -m "Housekeeping: rate limiter improvements and repo cleanup"
} catch {
  Warn "Nothing to commit or commit failed: $($_.Exception.Message)"
}

Info "Ensuring branch $Branch..."
git branch -M $Branch

Info "Fetching and pushing..."
git fetch $Remote --prune

git push $Remote $Branch

Good "Done. If push still hangs, clone to a non-OneDrive folder and push from there."
