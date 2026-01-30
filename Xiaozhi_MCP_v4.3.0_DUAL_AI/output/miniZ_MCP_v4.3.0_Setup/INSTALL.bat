@echo off
chcp 65001 >nul
title 🚀 miniZ MCP - Cài Đặt

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║         🚀 miniZ MCP v4.3.0 - Cài Đặt                    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Đang chạy với quyền Administrator...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Get install path
set INSTALL_PATH=%LOCALAPPDATA%\miniZ_MCP

echo 📁 Thư mục cài đặt: %INSTALL_PATH%
echo.

:: Create directory
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

:: Copy files
echo 📦 Đang sao chép files...
xcopy /E /Y /Q "%~dp0*" "%INSTALL_PATH%\" >nul

:: Create desktop shortcut
echo 🔗 Tạo shortcut Desktop...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\miniZ MCP.lnk'); $s.TargetPath = '%INSTALL_PATH%\miniZ_MCP.exe'; $s.WorkingDirectory = '%INSTALL_PATH%'; $s.Description = 'miniZ MCP - AI Control'; $s.Save()"

:: Create Start Menu shortcut
echo 🔗 Tạo shortcut Start Menu...
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\miniZ MCP
if not exist "%STARTMENU%" mkdir "%STARTMENU%"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU%\miniZ MCP.lnk'); $s.TargetPath = '%INSTALL_PATH%\miniZ_MCP.exe'; $s.WorkingDirectory = '%INSTALL_PATH%'; $s.Save()"

echo.
echo ✅ Cài đặt hoàn tất!
echo.
echo 🚀 Bạn có muốn chạy miniZ MCP ngay? (Y/N)
set /p RUN=

if /i "%RUN%"=="Y" (
    start "" "%INSTALL_PATH%\miniZ_MCP.exe"
)

echo.
echo 👋 Nhấn phím bất kỳ để đóng...
pause >nul
