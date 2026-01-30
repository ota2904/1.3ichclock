@echo off
chcp 65001 >nul
title miniZ MCP - Build Professional Installer (No Key Required)
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║    miniZ MCP Professional - Build Installer                ║
echo ║    Version: 4.3.5 (No License Key Required)                ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

:: Check if EXE exists
if not exist "dist\miniZ_MCP.exe" (
    echo ❌ ERROR: dist\miniZ_MCP.exe not found!
    echo.
    echo Please build EXE first:
    echo   .venv\Scripts\python.exe build_to_dist.py
    echo.
    pause
    exit /b 1
)

:: Check if Inno Setup exists
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo ❌ ERROR: Inno Setup 6 not found!
    echo.
    echo Please install Inno Setup 6 from:
    echo   https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo ✅ Found Inno Setup: %ISCC_PATH%
echo.

:: Create output directory
if not exist "installer_output" mkdir installer_output

:: Show file sizes
echo 📦 File to package:
for %%I in (dist\miniZ_MCP.exe) do echo    - miniZ_MCP.exe: %%~zI bytes

echo.
echo 🔨 Building installer...
echo.

:: Build installer
"%ISCC_PATH%" /Q "installer_professional_nokey.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════════╗
    echo ║                                                            ║
    echo ║              ✅ BUILD SUCCESSFUL!                          ║
    echo ║                                                            ║
    echo ╚════════════════════════════════════════════════════════════╝
    echo.
    echo 📦 Installer created:
    for %%I in (installer_output\miniZ_MCP_Professional_v4.3.5_Setup.exe) do (
        echo    Path: %%~fI
        echo    Size: %%~zI bytes
    )
    echo.
    echo ✨ Features:
    echo    - No license key required
    echo    - No API keys exposed
    echo    - Auto-activation on install
    echo    - 146+ AI tools included
    echo.
    echo 🚀 Ready to distribute!
    echo.
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo.
    echo Check the error messages above.
    echo.
)

pause
