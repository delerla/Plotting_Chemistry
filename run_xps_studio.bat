@echo off
setlocal
cd /d "%~dp0"

title XPS Studio - Dr. Deler Langenberg
color 0B

echo.
echo ==============================================================================
echo   XPS Studio: High-Resolution Core-Level Photoelectron Intelligence
echo   Lead: Dr. Deler Langenberg
echo ==============================================================================
echo.

set "PYTHON_EXE="

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;%PATH%"
) else (
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
    ) else (
        where python >nul 2>nul
        if %ERRORLEVEL% equ 0 (
            set "PYTHON_EXE=python"
        ) else (
            where py >nul 2>nul
            if %ERRORLEVEL% equ 0 (
                set "PYTHON_EXE=py"
            )
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python 3.12 was not found. Please run setup_environment.bat first.
    pause
    exit /b 1
)

echo [INFO] Python Interpreter: %PYTHON_EXE%

if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment .venv
    call .venv\Scripts\activate.bat
    set "PYTHON_EXE=python"
)

echo [1/2] Verifying XPS Studio environment...
%PYTHON_EXE% -c "import streamlit, lmfit, scipy, matplotlib, pandas, numpy" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing required dependencies...
    %PYTHON_EXE% -m pip install -r requirements.txt
)

echo [2/2] Launching XPS Studio Web Dashboard...
echo.
echo URL: http://localhost:8502
echo (Press Ctrl+C in this window to stop the server)
echo.

start "" http://localhost:8502
%PYTHON_EXE% -m streamlit run xps_studio/app_xps.py --server.port 8502 --server.headless false

pause
