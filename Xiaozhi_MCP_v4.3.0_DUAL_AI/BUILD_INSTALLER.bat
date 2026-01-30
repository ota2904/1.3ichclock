@echo off
chcp 65001 >nul
color 0B
title BUILD INNO SETUP INSTALLER

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║    📦 BUILD INNO SETUP INSTALLER - miniZ MCP v4.3.0        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check Inno Setup
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist %ISCC% (
    echo ❌ Inno Setup not found!
    echo.
    echo 📥 Download from: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo ✅ Inno Setup found
echo.

REM Check required files
echo [Checking files...]
if not exist "dist\miniZ_MCP_Professional.exe" (
    echo ❌ EXE file not found in dist folder
    pause
    exit /b 1
)
echo ✅ EXE file found

if not exist "installer_with_license.iss" (
    echo ❌ Installer script not found
    pause
    exit /b 1
)
echo ✅ Installer script found
echo.

REM Create output directory
if not exist "installer_output" mkdir "installer_output"

REM Build installer
echo [Building installer...]
echo.
%ISCC% "installer_with_license.iss"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Build FAILED!
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                   ✅ BUILD SUCCESSFUL!                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📦 Installer file:
echo    installer_output\miniZ_MCP_Professional_Setup_v4.3.0.exe
echo.
echo 🧪 Test với license key:
echo    MINIZ-STD2-UD5C-W3E4-6ESA
echo.
pause
