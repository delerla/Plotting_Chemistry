@echo off
setlocal enabledelayedexpansion

title GitHub Sync Tool - Materials Characterization Hub
echo ==============================================================================
echo  GitHub Synchronization Assistant
echo ==============================================================================
echo.

where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not in PATH.
    echo Please install Git for Windows from https://git-scm.com/
    pause
    exit /b 1
)

:: Ensure on main branch
git branch -M main >nul 2>nul

:: Check if remote origin exists
git remote get-url origin >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] No remote GitHub repository linked yet.
    echo.
    echo 1. Go to https://github.com/new and create a new repository (e.g., Plotting_Chemistry).
    echo 2. Copy the HTTPS or SSH repository URL.
    echo.
    set /p REPO_URL="Enter your GitHub repository URL: "
    if "!REPO_URL!"=="" (
        echo [ERROR] Repository URL cannot be empty.
        pause
        exit /b 1
    )
    git remote add origin !REPO_URL!
    echo [OK] Remote "origin" linked to: !REPO_URL!
    echo.
) else (
    for /f "tokens=*" %%u in ('git remote get-url origin') do set CURRENT_REMOTE=%%u
    echo [INFO] Linked GitHub repository: !CURRENT_REMOTE!
    echo.
)

:: Prompt for commit message
echo Enter a commit summary (or press Enter for automatic timestamp):
set /p COMMIT_MSG="Commit message: "
if "!COMMIT_MSG!"=="" (
    for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
    set COMMIT_MSG=Sync materials hub update !DT:~0,4!-!DT:~4,2!-!DT:~6,2! !DT:~8,2!:!DT:~10,2!
)

echo.
echo [1/3] Staging modified and new files...
git add -A

echo [2/3] Committing changes...
git commit -m "!COMMIT_MSG!"

echo [3/3] Synchronizing with GitHub (pull --rebase and push)...
git pull origin main --rebase 2>nul
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==============================================================================
    echo  [SUCCESS] Successfully synchronized with GitHub!
    echo ==============================================================================
) else (
    echo.
    echo [NOTICE] Push encountered an issue. If this is your first push to a newly
    echo          created empty repository, run:
    echo          git push -u origin main --force
)

echo.
pause
