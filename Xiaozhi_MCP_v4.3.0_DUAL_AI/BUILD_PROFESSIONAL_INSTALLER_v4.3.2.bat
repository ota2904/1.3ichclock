@echo off
chcp 65001 >nul
color 0B
title miniZ MCP v4.3.2 - Professional Installer Builder

echo.
echo ═══════════════════════════════════════════════════════════════════════
echo    miniZ MCP v4.3.2 - Professional Installer Builder
echo    3-Device MCP Support ^| License Security ^| Enterprise Ready
echo ═══════════════════════════════════════════════════════════════════════
echo.

:: Check if EXE exists
if not exist "dist\miniZ_MCP_v4.3.2_3Device.exe" (
    echo ❌ ERROR: EXE file not found!
    echo    Expected: dist\miniZ_MCP_v4.3.2_3Device.exe
    echo.
    echo    Please build the EXE first using PyInstaller
    echo.
    pause
    exit /b 1
)

:: Display EXE info
for %%A in (dist\miniZ_MCP_v4.3.2_3Device.exe) do (
    echo ✅ EXE Found: %%~nxA
    echo    Size: %%~zA bytes ^(~127 MB^)
    echo.
)

:: Check if Inno Setup is installed
set INNO_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %INNO_PATH% (
    set INNO_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
)

if not exist %INNO_PATH% (
    echo ❌ ERROR: Inno Setup 6 not found!
    echo.
    echo    Please install Inno Setup 6 from:
    echo    https://jrsoftware.org/isdl.php
    echo.
    echo    Expected locations:
    echo    - C:\Program Files ^(x86^)\Inno Setup 6\ISCC.exe
    echo    - C:\Program Files\Inno Setup 6\ISCC.exe
    echo.
    pause
    exit /b 1
)

echo ✅ Inno Setup found: %INNO_PATH%
echo.

:: Create output directory
if not exist "installer_output" mkdir installer_output
echo 📁 Output directory ready
echo.

:: Build installer
echo ═══════════════════════════════════════════════════════════════════════
echo    BUILDING PROFESSIONAL INSTALLER...
echo ═══════════════════════════════════════════════════════════════════════
echo.
echo 🔨 Starting Inno Setup compiler...
echo.

%INNO_PATH% "installer_professional_v4.3.2.iss" /Q

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ═══════════════════════════════════════════════════════════════════════
    echo    ❌ BUILD FAILED
    echo ═══════════════════════════════════════════════════════════════════════
    echo.
    echo    Error code: %ERRORLEVEL%
    echo    Check the Inno Setup script for errors
    echo.
    pause
    exit /b %ERRORLEVEL%
)

:: Check if installer was created
if not exist "installer_output\miniZ_MCP_v4.3.2_3Device_Professional_Setup.exe" (
    echo.
    echo ❌ Installer file not created!
    echo    Expected: installer_output\miniZ_MCP_v4.3.2_3Device_Professional_Setup.exe
    echo.
    pause
    exit /b 1
)

:: Display success information
echo.
echo ═══════════════════════════════════════════════════════════════════════
echo    ✅ BUILD SUCCESSFUL!
echo ═══════════════════════════════════════════════════════════════════════
echo.
echo 📦 INSTALLER INFORMATION:
echo.

for %%A in (installer_output\miniZ_MCP_v4.3.2_3Device_Professional_Setup.exe) do (
    echo    Filename: %%~nxA
    echo    Size: %%~zA bytes
    set size_mb=%%~zA
)

:: Calculate size in MB (approximate)
set /a size_mb=%size_mb% / 1048576
echo    Size: ~%size_mb% MB
echo    Location: %CD%\installer_output
echo.

echo 🎯 INSTALLER FEATURES:
echo    ✅ Professional Windows Installer
echo    ✅ License Activation System (Encrypted)
echo    ✅ Trial Version Support (30 days)
echo    ✅ 3-Device MCP Support
echo    ✅ Modern UI (Inno Setup 6)
echo    ✅ Desktop Shortcut Option
echo    ✅ Auto-Startup Option
echo    ✅ Start Menu Integration
echo    ✅ Firewall Auto-Configuration
echo    ✅ Registry Integration (Secure)
echo    ✅ Smart Uninstall (Keeps Config)
echo    ✅ Silent Install Support
echo    ✅ Password Protected (miniZ2025)
echo.

echo 📋 INCLUDED FILES:
echo    • miniZ_MCP_v4.3.2_3Device.exe (127 MB)
echo    • VERSION_v4.3.2_CHANGELOG.md
echo    • LICENSE_AGREEMENT.txt
echo    • Configuration Templates
echo    • License System (Encrypted)
echo    • Documentation (Guides)
echo.

echo 🔑 LICENSE KEY FORMAT:
echo    MINIZ-XXXXX-XXXXX-XXXXX-XXXXX
echo    (Leave empty for 30-day trial)
echo.

echo 🚀 READY TO DISTRIBUTE!
echo    Share: %CD%\installer_output\miniZ_MCP_v4.3.2_3Device_Professional_Setup.exe
echo.

echo 💡 INSTALLATION PASSWORD: miniZ2025
echo    (Encrypted installer - add extra security layer)
echo.

echo ═══════════════════════════════════════════════════════════════════════
echo.

:: Open output folder
echo Opening installer output folder...
explorer "installer_output"

echo.
echo Press any key to exit...
pause >nul
