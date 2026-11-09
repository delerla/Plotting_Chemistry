@echo off
setlocal enabledelayedexpansion

title Setup Scientific Python Environment
echo ==============================================================================
echo  Materials Characterization Hub - One-Click Environment Setup
echo ==============================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in PATH.
    echo Please install Python 3.10+ and check "Add Python to PATH".
    pause
    exit /b 1
)

echo [1/3] Creating isolated Python virtual environment (.venv)...
if not exist .venv (
    python -m venv .venv
    echo [OK] Virtual environment created in .venv\
) else (
    echo [INFO] Existing .venv detected.
)

echo [2/3] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [3/3] Installing mandatory scientific libraries from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==============================================================================
    echo  [SUCCESS] Environment setup complete!
    echo  You can now double-click "run_gui.bat" to start the Desktop Hub anytime.
    echo ==============================================================================
) else (
    echo.
    echo [ERROR] Encountered an error while installing requirements.
)

pause
