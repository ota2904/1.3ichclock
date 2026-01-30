@echo off
chcp 65001 >nul
title miniZ MCP v4.3.0 - Professional Installation
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║        miniZ MCP v4.3.0 - PROFESSIONAL EDITION          ║
echo ║              Tự Động Cài Đặt Đầy Đủ                     ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 🎯 Chức năng sẽ được cài:
echo    ✨ Smart Conversation Analyzer v1.0
echo    🎵 VLC Music Player Integration
echo    🌐 Multi-Device Sync (3 thiết bị)
echo    🤖 141 AI Tools
echo    💾 Conversation Memory System
echo    📊 Web Dashboard
echo.

:: Admin check
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Khuyến nghị chạy với quyền Administrator
    echo    (Để cài đầy đủ tính năng auto-startup)
    timeout /t 3 >nul
)

:: Kiểm tra Python
echo [1/7] Kiểm tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Chưa cài Python! 
    echo.
    echo 📥 Vui lòng cài Python 3.11+ từ:
    echo    https://python.org/downloads
    echo.
    echo 💡 Lưu ý: Tích "Add Python to PATH" khi cài
    pause
    start https://python.org/downloads
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version') do set PYTHON_VER=%%v
echo ✅ Python %PYTHON_VER% đã có sẵn
echo.

:: Kiểm tra pip
echo [2/7] Kiểm tra pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚙️  Pip chưa có! Đang cài đặt...
    python -m ensurepip --upgrade
    if errorlevel 1 (
        echo ❌ Không thể cài pip!
        pause
        exit /b 1
    )
)
for /f "tokens=2" %%v in ('pip --version') do set PIP_VER=%%v
echo ✅ Pip %PIP_VER% sẵn sàng
echo.

:: Upgrade pip
echo [3/7] Nâng cấp pip lên phiên bản mới nhất...
python -m pip install --upgrade pip --quiet
echo ✅ Pip đã được cập nhật
echo.

:: Check requirements.txt
echo [4/7] Kiểm tra requirements.txt...
if not exist requirements.txt (
    echo ❌ File requirements.txt không tồn tại!
    echo    Tạo file requirements.txt với nội dung cơ bản...
    echo fastapi==0.104.1 > requirements.txt
    echo uvicorn[standard]==0.24.0 >> requirements.txt
    echo psutil==5.9.6 >> requirements.txt
    echo websockets==12.0 >> requirements.txt
    echo pyautogui==0.9.54 >> requirements.txt
    echo pyperclip==1.8.2 >> requirements.txt
    echo python-vlc==3.0.18121 >> requirements.txt
    echo Pillow==10.1.0 >> requirements.txt
)
echo ✅ Requirements file OK
echo.

:: Cài đặt dependencies
echo [5/7] Đang cài đặt thư viện Python...
echo    📦 Core packages:
echo       • FastAPI + Uvicorn (Web framework)
echo       • psutil (System monitoring)
echo       • websockets (MCP connection)
echo    📦 Automation packages:
echo       • pyautogui (GUI automation)
echo       • pyperclip (Clipboard)
echo    📦 Media packages:
echo       • python-vlc (Music player)
echo       • Pillow (Image processing)
echo.
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ⚠️  Một số package gặp lỗi! Thử cài lại...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ Cài đặt thất bại!
        echo 📋 Kiểm tra kết nối mạng và thử lại
        pause
        exit /b 1
    )
)
echo ✅ Đã cài đặt xong tất cả thư viện
echo.

:: Verify installation
echo [6/7] Kiểm tra các thư viện...
python -c "import fastapi, uvicorn, psutil, websockets; print('✅ Core packages OK')" 2>nul
if errorlevel 1 (
    echo ❌ Core packages có vấn đề!
    pause
    exit /b 1
)
python -c "import pyautogui, pyperclip; print('✅ Automation packages OK')" 2>nul
python -c "import vlc, PIL; print('✅ Media packages OK')" 2>nul
echo.

:: Create config if not exists
echo [7/7] Kiểm tra cấu hình...
if not exist xiaozhi_endpoints.json (
    echo 📝 Tạo file config mẫu...
    echo [ > xiaozhi_endpoints.json
    echo   {"name": "Thiết bị 1", "token": "", "enabled": true}, >> xiaozhi_endpoints.json
    echo   {"name": "Thiết bị 2", "token": "", "enabled": false}, >> xiaozhi_endpoints.json
    echo   {"name": "Thiết bị 3", "token": "", "enabled": false} >> xiaozhi_endpoints.json
    echo ] >> xiaozhi_endpoints.json
)
echo ✅ Config đã sẵn sàng
echo.

echo ╔══════════════════════════════════════════════════════════╗
echo ║                  🎉 CÀI ĐẶT THÀNH CÔNG!                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.
echo 📊 Thống kê:
python -c "import sys; print(f'   • Python: {sys.version.split()[0]}')"
python -c "import fastapi; print(f'   • FastAPI: {fastapi.__version__}')"
python -c "import uvicorn; print(f'   • Uvicorn: {uvicorn.__version__}')"
echo    • Smart Analyzer: v1.0
echo    • Tools: 141 functions
echo.
echo 📋 Bước tiếp theo:
echo.
echo    1️⃣  Lấy JWT token:
echo       • Mở: https://xiaozhi.me/console
echo       • Đăng nhập và copy token
echo.
echo    2️⃣  Khởi động server:
echo       • Chạy: START.bat
echo       • Hoặc: python xiaozhi_final.py
echo.
echo    3️⃣  Cấu hình token:
echo       • Mở: http://localhost:8000
echo       • Vào tab "Cấu hình"
echo       • Dán token và Save
echo.
echo    4️⃣  (Optional) Build EXE:
echo       • Chạy: BUILD_EXE.bat
echo       • Tạo file exe độc lập
echo.
echo 💡 Tài liệu:
echo    • README.md - Hướng dẫn chi tiết
echo    • SMART_ANALYZER_GUIDE.md - Smart Analyzer
echo    • CONVERSATION_MEMORY_ARCHITECTURE.md - Memory system
echo.
echo 🚀 Nhấn phím bất kỳ để khởi động ngay...
pause >nul

:: Start server
cls
echo Đang khởi động miniZ MCP...
START.bat
