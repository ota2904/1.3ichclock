@echo off
chcp 65001 >nul
title 🚀 miniZ MCP Full Features - Cài Đặt

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     🚀 miniZ MCP v4.3.0 - Full Features Edition       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set INSTALL_PATH=%LOCALAPPDATA%\miniZ_MCP_Full

echo 📁 Thư mục cài đặt: %INSTALL_PATH%
echo.

:: Create directory
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

:: Copy files
echo 📦 Đang sao chép files...
xcopy /E /Y /Q "%~dp0*" "%INSTALL_PATH%\" >nul

:: Create desktop shortcut
echo 🔗 Tạo shortcut Desktop...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\miniZ MCP Full.lnk'); $s.TargetPath = '%INSTALL_PATH%\miniZ_MCP_Full.exe'; $s.WorkingDirectory = '%INSTALL_PATH%'; $s.Description = 'miniZ MCP Full Features'; $s.Save()"

:: Create Start Menu shortcut
echo 🔗 Tạo shortcut Start Menu...
set STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\miniZ MCP Full
if not exist "%STARTMENU%" mkdir "%STARTMENU%"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU%\miniZ MCP Full.lnk'); $s.TargetPath = '%INSTALL_PATH%\miniZ_MCP_Full.exe'; $s.WorkingDirectory = '%INSTALL_PATH%'; $s.Save()"

:: Enable auto-start (tự động)
echo 🚀 Bật khởi động cùng Windows...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP_Full" /t REG_SZ /d ""%INSTALL_PATH%\miniZ_MCP_Full.exe" --hidden" /f >nul 2>&1

echo.
echo ✅ Cài đặt hoàn tất!
echo.
echo ✨ TÍNH NĂNG ĐẶC BIỆT:
echo    • API keys được lưu tự động
echo    • Khởi động cùng Windows (đã bật)
echo    • Không cần cấu hình lại
echo.
echo 🚀 Chạy ngay? (Y/N)
set /p RUN=

if /i "%RUN%"=="Y" (
    start "" "%INSTALL_PATH%\miniZ_MCP_Full.exe"
)

echo.
echo 👋 Nhấn phím bất kỳ để đóng...
pause >nul
