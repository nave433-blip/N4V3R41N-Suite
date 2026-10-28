@echo off
REM build-windows.bat — build N4V3R41N-CLI natively on Windows.
REM (Windows equivalent of the old Unix build shell steps.)
REM Requires: Rust via rustup (cargo on PATH) + the Visual Studio
REM Build Tools (C++ workload) for the MSVC linker.
REM Double-click it, or run it from cmd in the scripts folder.

where cargo >nul 2>nul
if errorlevel 1 (
    echo cargo not found. Install Rust from https://rustup.rs/ and re-run.
    pause
    exit /b 1
)

cd /d "%~dp0..\src\rust"
cargo build --release
if errorlevel 1 (
    echo.
    echo BUILD FAILED — see the errors above.
    pause
    exit /b 1
)

if not exist "%~dp0..\dist" mkdir "%~dp0..\dist"
copy /y "target\release\n4v3r41n-cli.exe" "%~dp0..\dist\n4v3r41n-cli.exe"
echo.
echo Built: dist\n4v3r41n-cli.exe
pause
