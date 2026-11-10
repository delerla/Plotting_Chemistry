# ==============================================================================
# launch_gui.ps1 - Native Windows PowerShell Launcher for Materials Hub
# ==============================================================================

$Host.UI.RawUI.WindowTitle = "Materials Characterization Hub - Desktop GUI"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Resolve real Python interpreter (bypass WindowsApps dummy alias)
$pythonPath = $null
$pyCmd = Get-Command python -ErrorAction SilentlyContinue
if ($pyCmd -and $pyCmd.Source -notlike "*WindowsApps*") {
    $pythonPath = $pyCmd.Source
}

if (-not $pythonPath) {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python311\python.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $pythonPath = $cand
            break
        }
    }
}

if (-not $pythonPath) {
    Write-Host "[ERROR] Python 3.10+ not found in PATH or standard installation folders." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/ and check 'Add Python to PATH'."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[INFO] Using Python interpreter: $pythonPath" -ForegroundColor Cyan

# 2. Activate virtualenv if present
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment (.venv)..." -ForegroundColor Cyan
    . ".venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment (venv)..." -ForegroundColor Cyan
    . "venv\Scripts\Activate.ps1"
}

# 3. Check Streamlit installation
$streamlitInstalled = & $pythonPath -c "import streamlit" 2>$null; $?
if (-not $streamlitInstalled) {
    Write-Host "[INFO] Dependencies missing. Installing from requirements.txt..." -ForegroundColor Yellow
    & $pythonPath -m pip install --upgrade pip
    & $pythonPath -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to install dependencies." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "[INFO] Starting Streamlit server at http://localhost:8501..." -ForegroundColor Green
Write-Host "[INFO] Opening default web browser..." -ForegroundColor Green

# 4. Open browser
Start-Process "http://localhost:8501"

# 5. Launch Streamlit
& $pythonPath -m streamlit run app.py --server.port=8501 --server.headless=true
