# PowerShell helper to run the FastAPI app with the project's venv python
# Usage: .\run_server.ps1 [-Module main_optimized:app] [-BindHost 127.0.0.1] [-Port 8000]
param(
    [string]$Module = "main_optimized:app",
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000
)

$venvPy = Join-Path -Path $PSScriptRoot -ChildPath ".venv\Scripts\python.exe"
if (-Not (Test-Path $venvPy)) {
    Write-Error "Python executable not found at $venvPy. Activate your venv or adjust path."
    exit 1
}

# Ensure .env loaded by run.py
$env:APP_MODULE = $Module
$env:HOST = $BindHost
$env:PORT = [string]$Port

& $venvPy -u .\run.py $BindHost $Port
