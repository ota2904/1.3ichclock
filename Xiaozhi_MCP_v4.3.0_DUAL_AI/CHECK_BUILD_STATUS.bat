@echo off
chcp 65001 > nul
title Build Status Check
:loop
cls
echo.
echo ================================================================
echo 🔍 CHECKING BUILD STATUS
echo ================================================================
echo.
echo Time: %TIME%
echo.

if exist "dist\miniZ_MCP_v4.3.1_FINAL_FIXED.exe" (
    echo ✅ EXE FILE FOUND!
    echo.
    for %%F in ("dist\miniZ_MCP_v4.3.1_FINAL_FIXED.exe") do (
        set /a size_mb=%%~zF / 1048576
        echo 📁 File: miniZ_MCP_v4.3.1_FINAL_FIXED.exe
        echo 📊 Size: !size_mb! MB
        echo 📅 Date: %%~tF
    )
    echo.
    echo ================================================================
    echo 🎉 BUILD COMPLETE!
    echo ================================================================
    echo.
    pause
    explorer dist
    exit
) else (
    echo ⏳ Building... (checking every 10 seconds)
    echo.
    
    REM Check if python PyInstaller is running
    tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo 🔨 PyInstaller is running...
    ) else (
        echo ⚠️  Python not found. Build may have stopped.
        echo.
        pause
        exit
    )
)

echo.
echo Press Ctrl+C to stop checking, or wait...
timeout /t 10 /nobreak >nul
goto loop
