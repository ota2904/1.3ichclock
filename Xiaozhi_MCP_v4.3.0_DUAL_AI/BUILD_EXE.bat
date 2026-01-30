@echo off
chcp 65001 >nul
title 🚀 miniZ MCP - Professional Build System
color 0B

echo ╔══════════════════════════════════════════════════════════╗
echo ║         🚀 miniZ MCP Installer Builder v4.3.0            ║
echo ║              Professional Edition with:                  ║
echo ║              • System Tray Support                       ║
echo ║              • Auto Startup                              ║
echo ║              • Smart Analyzer v1.0                       ║
echo ║              • Multi-Device Sync                         ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Admin check
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Khuyến nghị chạy với quyền Administrator để build đầy đủ
    echo    (Nhấn phím bất kỳ để tiếp tục...)
    pause >nul
)

:: Check Python
echo [1/6] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được cài đặt!
    echo 📥 Tải về: https://python.org (Python 3.11+)
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version') do set PYTHON_VER=%%v
echo ✅ Python %PYTHON_VER%
echo.

:: Check PyInstaller
echo [2/6] Kiểm tra PyInstaller...
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Đang cài đặt PyInstaller...
    pip install pyinstaller --quiet
)
echo ✅ PyInstaller sẵn sàng
echo.

:: Install dependencies
echo [3/6] Cài đặt dependencies cho EXE...
echo    • pystray (System tray)
echo    • Pillow (Icon handling)
echo    • pywin32 (Windows integration)
pip install pyinstaller pystray Pillow pywin32 --quiet --disable-pip-version-check
if errorlevel 1 (
    echo ⚠️  Một số package không cài được (tiếp tục...)
)
echo ✅ Dependencies đã cài
echo.

:: Check requirements
echo [4/6] Kiểm tra requirements.txt...
if not exist requirements.txt (
    echo ❌ File requirements.txt không tồn tại!
    pause
    exit /b 1
)
echo ✅ Requirements OK
echo.

:: Build
echo [5/6] Building EXE với PyInstaller...
echo    📁 Output: dist\miniZ_MCP.exe
echo.
python build_installer.py
if errorlevel 1 (
    echo.
    echo ❌ Build thất bại!
    echo 📋 Kiểm tra log bên trên để debug
    pause
    exit /b 1
)
echo.

:: Verify output
echo [6/6] Kiểm tra output...
if exist "dist\miniZ_MCP.exe" (
    echo ✅ EXE đã được tạo thành công!
    echo.
    echo 📊 Thông tin file:
    for %%F in ("dist\miniZ_MCP.exe") do echo    Size: %%~zF bytes
    echo    Path: %CD%\dist\miniZ_MCP.exe
) else (
    echo ❌ Không tìm thấy file EXE!
    pause
    exit /b 1
)

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                  🎉 BUILD THÀNH CÔNG!                    ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 📦 Các file đã tạo:
echo    • dist\miniZ_MCP.exe (Main executable)
if exist "dist\miniZ_MCP_installer.exe" (
    echo    • dist\miniZ_MCP_installer.exe (Windows Installer)
)
echo.
echo 🚀 Các tính năng trong EXE:
echo    ✅ Web Dashboard (http://localhost:8000)
echo    ✅ System Tray với icon
echo    ✅ Auto startup Windows
echo    ✅ Smart Conversation Analyzer
echo    ✅ 141 Tools hỗ trợ
echo    ✅ Multi-device sync
echo    ✅ VLC Music Player control
echo.
echo 📋 Bước tiếp theo:
echo    1. Test: Chạy dist\miniZ_MCP.exe
echo    2. Deploy: Copy toàn bộ folder dist
echo    3. Share: Nén thành ZIP và chia sẻ
echo.
echo 💡 Mẹo:
echo    • Thêm --hidden để chạy ngầm
echo    • Chuột phải icon tray để menu
echo    • Config tại http://localhost:8000
echo.
echo ✨ Nhấn phím bất kỳ để mở folder dist...
pause >nul
explorer dist
