<#
.SYNOPSIS
    Automated GitHub synchronization tool for Materials Characterization Hub.
#>

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host " GitHub Synchronization Assistant - Materials Characterization Hub" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan

# 1. Check Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed or not in PATH. Please install Git from https://git-scm.com/"
    exit 1
}

# 2. Ensure main branch
git branch -M main 2>$null

# 3. Check / configure remote
$remoteUrl = git remote get-url origin 2>$null
if (-not $remoteUrl) {
    Write-Host "`n[INFO] No remote repository linked yet." -ForegroundColor Yellow
    Write-Host "1. Create a repository on https://github.com/new (e.g., Plotting_Chemistry)"
    Write-Host "2. Copy the URL (e.g., https://github.com/username/Plotting_Chemistry.git)"
    $repoInput = Read-Host "`nEnter GitHub Repository URL"
    if ([string]::IsNullOrWhiteSpace($repoInput)) {
        Write-Error "Repository URL cannot be empty."
        exit 1
    }
    git remote add origin $repoInput.Trim()
    Write-Host "[OK] Linked remote origin to $repoInput" -ForegroundColor Green
} else {
    Write-Host "`n[INFO] Linked repository: $remoteUrl" -ForegroundColor Green
}

# 4. Commit message
$defaultMsg = "Sync materials characterization updates $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
$userMsg = Read-Host "`nEnter commit message (press Enter for: '$defaultMsg')"
$commitMsg = if ([string]::IsNullOrWhiteSpace($userMsg)) { $defaultMsg } else { $userMsg }

# 5. Stage, commit, and push
Write-Host "`n[1/3] Staging changes..." -ForegroundColor Cyan
git add -A

Write-Host "[2/3] Committing changes..." -ForegroundColor Cyan
git commit -m $commitMsg

Write-Host "[3/3] Syncing with GitHub..." -ForegroundColor Cyan
git pull origin main --rebase 2>$null
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n==============================================================================" -ForegroundColor Green
    Write-Host " [SUCCESS] Successfully synchronized with GitHub!" -ForegroundColor Green
    Write-Host "==============================================================================" -ForegroundColor Green
} else {
    Write-Host "`n[NOTICE] If this is the initial push to a fresh repository, run:" -ForegroundColor Yellow
    Write-Host "git push -u origin main --force" -ForegroundColor White
}
