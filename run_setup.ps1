<#
.SYNOPSIS
All-in-One Setup & Launcher for Raju's Royal Artifacts Shop (Windows PowerShell)

.DESCRIPTION
Checks prerequisites, initializes venv, installs dependencies, runs tests,
sets GEMINI_API_KEY, launches the server, and opens the Web UI.
#>

$ErrorActionPreference = "Stop"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Raju's Royal Artifacts - All-in-One Windows Setup      " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Prerequisite Check: Python

Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
$pythonCmd = "python"

if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $pyVer = & python --version 2>&1
    Write-Host "[+] Using system Python: $pyVer" -ForegroundColor Green
}
elseif (Test-Path "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe") {
    $pythonCmd = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe"
    Write-Host "[+] Using Cloud SDK Python: $pythonCmd" -ForegroundColor Green
}
else {
    Write-Error "[-] Python is not installed or not found in PATH! Please install Python 3.10+."
    exit 1
}

# 2. Check GEMINI_API_KEY

Write-Host ""
Write-Host "[2/5] Checking GEMINI_API_KEY..." -ForegroundColor Yellow

if (-not $env:GEMINI_API_KEY -and (Test-Path ".env")) {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*GEMINI_API_KEY\s*=\s*(.+)$") {
            $env:GEMINI_API_KEY = $matches[1].Trim()
        }
    }
}

if (-not $env:GEMINI_API_KEY) {
    Write-Host "[!] GEMINI_API_KEY is not set." -ForegroundColor Yellow

    $userKey = Read-Host "Please enter your Gemini API Key"

    if (-not [string]::IsNullOrWhiteSpace($userKey)) {
        $env:GEMINI_API_KEY = $userKey.Trim()

        Set-Content -Path ".env" -Value "GEMINI_API_KEY=$($env:GEMINI_API_KEY)"

        Write-Host "[+] Saved API key to .env file." -ForegroundColor Green
    }
}
else {
    Write-Host "[+] GEMINI_API_KEY is configured." -ForegroundColor Green
}

# 3. Virtual Environment & Dependencies

Write-Host ""
Write-Host "[3/5] Setting up Virtual Environment (.venv)..." -ForegroundColor Yellow

if (-not (Test-Path ".venv")) {
    & $pythonCmd -m venv .venv
    Write-Host "[+] Created virtual environment." -ForegroundColor Green
}

$venvPython = ".\.venv\Scripts\python.exe"

Write-Host "[+] Installing/Updating dependencies..." -ForegroundColor Yellow

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "[+] Dependencies installed successfully." -ForegroundColor Green

# 4. Run Tests

Write-Host ""
Write-Host "[4/5] Running automated tests..." -ForegroundColor Yellow

$env:PYTHONPATH = "."

& $venvPython -m pytest tests/test_agent.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "[+] All tests passed!" -ForegroundColor Green
}
else {
    Write-Host "[!] Tests encountered issues, continuing server launch..." -ForegroundColor Yellow
}

# 5. Launch FastAPI Server

Write-Host ""
Write-Host "[5/5] Launching Raju's Shop Server at http://localhost:8000" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "Press CTRL+C to stop the server." -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan

# Open browser
Start-Process "http://localhost:8000"

# Start server
& $venvPython -m uvicorn app.fast_api_app:app --host 127.0.0.1 --port 8000
