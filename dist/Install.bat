@echo off
REM N4V3R41N-Suite one-click launcher (double-click this file).
REM No terminal knowledge needed: it unblocks the downloaded files,
REM runs the PowerShell installer with the execution policy bypassed,
REM and leaves the window open so you can read the result.
REM
REM If you have the setup exe (N4V3R41N-Setup-*.exe), use that instead
REM - this file is the fallback for the zip download.

cd /d "%~dp0"

REM Strip the "downloaded from the internet" mark so Windows does not
REM silently block the script or the exe.
powershell -NoProfile -Command "Get-ChildItem -Path '%~dp0' -Filter *.ps1 | Unblock-File -ErrorAction SilentlyContinue; Unblock-File -Path '%~dp0n4v3r41n-cli.exe' -ErrorAction SilentlyContinue"

REM Run the installer. The pause at the end keeps the window open.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
echo.
echo ============================================================
echo  Done. If it says the install finished, open a NEW terminal
echo  (or use the Start Menu shortcut) and run: n4v3r41n-cli doctor
echo ============================================================
echo.
pause
