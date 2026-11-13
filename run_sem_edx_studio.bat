@echo off
setlocal
cd /d "%~dp0"

title SEM-EDX Studio - Dr. Deler Langenberg
color 0B

echo.
echo ==============================================================================
echo   SEM-EDX Studio: Microstructural Sizing & Elemental Quantification Suite
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

echo [INFO] Launching SEM-EDX Studio on http://localhost:8506 ...
echo.

"%PYTHON_EXE%" -m streamlit run sem_edx_studio\app_sem_edx.py --server.port 8506 --server.headless false --browser.gatherUsageStats false

pause
