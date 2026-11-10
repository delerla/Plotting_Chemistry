@echo off
setlocal
cd /d "%~dp0"

title Materials Characterization Hub - Desktop GUI
echo ==============================================================================
echo  Automated Materials Characterization ^& Spectroscopic Analysis Hub
echo ==============================================================================
echo.

rem Prefer explicit user python path if present to bypass WindowsApps execution alias
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
    echo [ERROR] Python was not found in PATH or standard installation folders.
    echo Please install Python 3.10+ from python.org and check Add Python to PATH.
    echo.
    pause
    exit /b 1
)

echo [INFO] Python interpreter: %PYTHON_EXE%

rem Activate virtualenv if present
if exist .venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment .venv
    call .venv\Scripts\activate.bat
    set "PYTHON_EXE=python"
) else (
    if exist venv\Scripts\activate.bat (
        echo [INFO] Activating virtual environment venv
        call venv\Scripts\activate.bat
        set "PYTHON_EXE=python"
    )
)

rem Check streamlit
%PYTHON_EXE% -c "import streamlit" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing dependencies from requirements.txt
    %PYTHON_EXE% -m pip install --upgrade pip
    %PYTHON_EXE% -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo [INFO] Opening default web browser at http://localhost:8501
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8501"

echo [INFO] Launching Streamlit Server...
%PYTHON_EXE% -m streamlit run app.py --server.port=8501 --server.headless=true

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Streamlit exited with an error.
    pause
)
