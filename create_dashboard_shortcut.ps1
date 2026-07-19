<#
.SYNOPSIS
    One-time setup: creates a "Finance Dashboard" shortcut on your Desktop
    that launches start_dashboard.ps1.

.USAGE
    Run this once:  .\create_dashboard_shortcut.ps1
    Then double-click "Finance Dashboard" on your Desktop whenever you want
    to open the dashboard.
#>

$ProjectDir = $PSScriptRoot
$TargetScript = Join-Path $ProjectDir "start_dashboard.ps1"
$ShortcutPath = Join-Path ([Environment]::GetFolderPath("Desktop")) "Finance Dashboard.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$TargetScript`""
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.IconLocation = "shell32.dll,43"
$Shortcut.Description = "Start the personal finance dashboard"
$Shortcut.Save()

Write-Host "Shortcut created: $ShortcutPath"
