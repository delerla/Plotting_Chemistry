@echo off
setlocal
cd /d "%~dp0"

title UV-Vis Studio - Dr. Deler Langenberg
color 0E

echo.
echo ==============================================================================
echo   UV-Vis Studio: Photokinetics, Tauc Optical Bandgap & Defect Suite
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
    echo [ERROR] Python was not found. Please run setup_environment.bat first.
    pause
    exit /b 1
)

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    set "PYTHON_EXE=python"
)

echo [INFO] Launching UV-Vis Studio on http://localhost:8505 ...
echo.

"%PYTHON_EXE%" -m streamlit run uv_vis_studio\app_uv_vis.py --server.port 8505 --server.headless false --browser.gatherUsageStats false

pause
