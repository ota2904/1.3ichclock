@echo off
chcp 65001 >nul
title 🗑️ miniZ MCP - Gỡ Cài Đặt

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         🗑️ miniZ MCP - Gỡ Cài Đặt                        ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set INSTALL_PATH=%LOCALAPPDATA%\miniZ_MCP

echo ⚠️  Bạn có chắc muốn gỡ cài đặt miniZ MCP? (Y/N)
set /p CONFIRM=

if /i not "%CONFIRM%"=="Y" (
    echo Đã hủy.
    pause
    exit /b
)

:: Kill running process
taskkill /F /IM miniZ_MCP.exe 2>nul

:: Remove from startup
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP" /f 2>nul

:: Remove shortcuts
del /f /q "%USERPROFILE%\Desktop\miniZ MCP.lnk" 2>nul
rmdir /s /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\miniZ MCP" 2>nul

:: Remove install directory
rmdir /s /q "%INSTALL_PATH%" 2>nul

echo.
echo ✅ Đã gỡ cài đặt miniZ MCP!
echo.
pause
