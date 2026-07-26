# setup_project.ps1 - Setup script for Windows PowerShell
# Run from repository root

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " RAG-Shield Windows Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Locate Python
Write-Host "==> 1/5 Checking Python installation..." -ForegroundColor Yellow
$pythonExe = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonExe) {
    Write-Error "Python was not found on your PATH. Please install Python (3.11 or later recommended)."
    Exit 1
}

$version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "    Found Python version: $version"

# 2. Rebuild virtual environment
Write-Host "==> 2/5 Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "    Created virtual environment in .venv"
} else {
    Write-Host "    Virtual environment .venv already exists."
}

# 3. Upgrade pip and install dependencies
Write-Host "==> 3/5 Installing demo dependencies..." -ForegroundColor Yellow
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-demo.txt

# 4. Smoke test
Write-Host "==> 4/5 Running CLI smoke test..." -ForegroundColor Yellow
$env:DEMO_MODE="1"
.\.venv\Scripts\python.exe .\demo_cli.py "Who founded Tesla Motors?"

# 5. Done
Write-Host "============================================================" -ForegroundColor Green
Write-Host " SETUP COMPLETE!" -ForegroundColor Green
Write-Host " To start the demo GUI, run:" -ForegroundColor White
Write-Host "     .\run_demo.ps1" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
