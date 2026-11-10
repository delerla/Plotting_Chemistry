# ==============================================================================
# PowerShell Script to Create a Windows Desktop Shortcut
# ==============================================================================

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path -Path $DesktopPath -ChildPath "Materials Characterization Hub.lnk"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ScriptDir) {
    $ScriptDir = "D:\Plotting_Chemistry"
}

$TargetPath = Join-Path -Path $ScriptDir -ChildPath "run_gui.bat"

# Remove old shortcut if exists
if (Test-Path $ShortcutPath) {
    Remove-Item -Force $ShortcutPath
}

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "Open-Source Materials Characterization & Spectroscopic Analysis Hub"
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,238"  # Scientific microscope icon
$Shortcut.Save()

Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Desktop Shortcut created successfully at:" -ForegroundColor Green
Write-Host " $ShortcutPath" -ForegroundColor Cyan
Write-Host " Target: $TargetPath" -ForegroundColor White
Write-Host " Working Directory: $ScriptDir" -ForegroundColor White
Write-Host "==============================================================================" -ForegroundColor Green
