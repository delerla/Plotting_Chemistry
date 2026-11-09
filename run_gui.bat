@echo off
setlocal enabledelayedexpansion

title Materials Characterization Hub - Desktop GUI
echo ==============================================================================
echo  Automated Materials Characterization ^& Spectroscopic Analysis Hub
echo ==============================================================================
echo.

:: Check for python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in PATH.
    echo Please install Python 3.10+ from python.org and check "Add Python to PATH".
    pause
    exit /b 1
)

:: Activate virtualenv if present
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment (venv)...
    call venv\Scripts\activate.bat
)

:: Verify streamlit
python -c "import streamlit" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Dependencies missing. Installing from requirements.txt...
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo [INFO] Launching Desktop GUI...
echo [INFO] Press Ctrl+C in this terminal to stop the server.
echo.

streamlit run app.py

pause
