# ==============================================================================
# PowerShell Script to Create a Windows Desktop Shortcut
# ==============================================================================

$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path -Path $DesktopPath -ChildPath "Materials Characterization Hub.lnk"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TargetPath = Join-Path -Path $ScriptDir -ChildPath "run_gui.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.Description = "Open-Source Materials Characterization & Spectroscopic Analysis Hub"
$Shortcut.IconLocation = "%SystemRoot%\System32\shell32.dll,238"  # Professional microscope/graph icon
$Shortcut.Save()

Write-Host "==============================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Desktop Shortcut created successfully at:" -ForegroundColor Green
Write-Host " $ShortcutPath" -ForegroundColor Cyan
Write-Host " You can now launch the Hub anytime directly from your Desktop!" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
