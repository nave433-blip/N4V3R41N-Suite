<#
.SYNOPSIS
    Installer for N4V3R41N-Suite (Windows).

.DESCRIPTION
    Places n4v3r41n-cli.exe into %LocalAppData%\N4V3R41N\bin, adds that
    folder to the current user's PATH (no admin rights needed), and
    verifies the install with `n4v3r41n-cli --version`.

    Run from the folder containing this script and n4v3r41n-cli.exe:
        powershell -ExecutionPolicy Bypass -File .\install.ps1

.NOTES
    - No administrator rights required (user-level install).
    - Re-running the installer updates the exe in place.
#>
[CmdletBinding()]
param(
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "N4V3R41N\bin")
)

$ErrorActionPreference = "Stop"

function Write-Step([string]$msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok([string]$msg)   { Write-Host "  [ok] $msg" -ForegroundColor Green }
function Write-Warn([string]$msg) { Write-Host "  [warn] $msg" -ForegroundColor Yellow }
function Fail([string]$msg)       { Write-Host "  [fail] $msg" -ForegroundColor Red; exit 1 }

Write-Step "N4V3R41N-Suite installer"

# 1. Locate the exe next to this script.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sourceExe = Join-Path $scriptDir "n4v3r41n-cli.exe"
if (-not (Test-Path $sourceExe)) {
    Fail "n4v3r41n-cli.exe not found next to install.ps1 (looked in $scriptDir)."
}
Write-Ok "found n4v3r41n-cli.exe"

# 2. Copy into the install dir.
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item -Force $sourceExe (Join-Path $InstallDir "n4v3r41n-cli.exe")
Write-Ok "installed to $InstallDir"

# 3. Add to the user's PATH if not already there.
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$pathEntries = $userPath -split ";" | ForEach-Object { $_.TrimEnd("\") }
if ($pathEntries -notcontains $InstallDir.TrimEnd("\")) {
    $newPath = if ([string]::IsNullOrWhiteSpace($userPath)) { $InstallDir } else { "$userPath;$InstallDir" }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Ok "added $InstallDir to user PATH"
    Write-Warn "open a NEW terminal for the PATH change to take effect"
} else {
    Write-Ok "$InstallDir already on user PATH"
}

# 4. Verify: run the freshly installed exe directly (no PATH dependency).
$installedExe = Join-Path $InstallDir "n4v3r41n-cli.exe"
Write-Step "Verifying installation"
try {
    $versionOut = & $installedExe --version 2>&1 | Out-String
} catch {
    Fail "installed exe failed to run: $_"
}
if ($versionOut -match "N4V3R41N") {
    Write-Ok "verification passed: $($versionOut.Trim())"
} else {
    Fail "unexpected --version output: $versionOut"
}

Write-Host ""
Write-Host "Done. Try:  n4v3r41n-cli doctor" -ForegroundColor Green
Write-Host ""
Write-Host "USB driver note: DFU-mode devices (05ac:1227) need the WinUSB" -ForegroundColor Yellow
Write-Host "driver on Windows. Install it with Zadig (https://zadig.akeo.ie/):" -ForegroundColor Yellow
Write-Host "  1. Put the device in DFU mode (black screen)." -ForegroundColor Yellow
Write-Host "  2. In Zadig, select the 'Apple Mobile Device (DFU Mode)' entry." -ForegroundColor Yellow
Write-Host "  3. Install the WinUSB driver for it." -ForegroundColor Yellow
Write-Host "Docs: WINDOWS.txt (build notes and limitations)" -ForegroundColor DarkGray
