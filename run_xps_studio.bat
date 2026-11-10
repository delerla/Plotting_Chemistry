@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: XPS Studio Launcher - Materials-Specific Spectroscopic Intelligence Hub
:: Authored & Maintained by Dr. Deler Langenberg (2026)
:: ============================================================================

title XPS Studio - Dr. Deler Langenberg
color 0B

echo.
echo ============================================================================
echo   XPS Studio: High-Resolution Core-Level Photoelectron Intelligence
echo   Lead: Dr. Deler Langenberg
echo ============================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Check for .venv first
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
    goto :LAUNCH
)

:: Check system Python 3.12
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_EXE=python"
    goto :LAUNCH
)

echo [ERROR] Python 3.12 was not found. Please run setup_environment.bat first.
pause
exit /b 1

:LAUNCH
echo [1/2] Verifying XPS Studio environment...
"%PYTHON_EXE%" -c "import streamlit, lmfit, scipy, matplotlib, pandas, numpy" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing required XPS dependencies...
    "%PYTHON_EXE%" -m pip install -r requirements.txt
)

echo [2/2] Launching XPS Studio Web Dashboard...
echo.
echo URL: http://localhost:8502
echo (Press Ctrl+C in this window to stop the server)
echo.

start "" http://localhost:8502
"%PYTHON_EXE%" -m streamlit run xps_studio/app_xps.py --server.port 8502 --server.headless false

pause
