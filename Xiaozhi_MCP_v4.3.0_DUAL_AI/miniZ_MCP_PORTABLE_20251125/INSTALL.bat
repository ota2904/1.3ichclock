@echo off
chcp 65001 >nul
title miniZ MCP - CÀI ĐẶT TỰ ĐỘNG
color 0A

echo ================================================================================
echo                    🌳 miniZ MCP v4.3.0 - CÀI ĐẶT TỰ ĐỘNG
echo ================================================================================
echo.
echo Đang kiểm tra hệ thống...
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ LỖI: Python chưa được cài đặt!
    echo.
    echo 📥 Vui lòng tải và cài Python từ: https://www.python.org/downloads/
    echo ⚠️  QUAN TRỌNG: Tick "Add Python to PATH" khi cài đặt
    echo.
    pause
    exit /b 1
)

echo ✅ Python đã được cài đặt
python --version
echo.

REM Kiểm tra pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ LỖI: pip chưa được cài đặt!
    echo.
    echo Đang cài đặt pip...
    python -m ensurepip --default-pip
    if %errorlevel% neq 0 (
        echo ❌ Không thể cài pip. Vui lòng cài thủ công.
        pause
        exit /b 1
    )
)

echo ✅ pip đã sẵn sàng
echo.

REM Upgrade pip
echo 🔄 Đang nâng cấp pip lên phiên bản mới nhất...
python -m pip install --upgrade pip --quiet
echo.

REM Cài đặt dependencies
echo 📦 Đang cài đặt các Python packages...
echo    (Quá trình này có thể mất 3-5 phút)
echo.

python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ LỖI: Không thể cài đặt một số packages!
    echo.
    echo 🔧 Thử các giải pháp sau:
    echo    1. Chạy CMD với quyền Administrator
    echo    2. Kiểm tra kết nối Internet
    echo    3. Chạy: python -m pip install --upgrade pip
    echo    4. Chạy lại INSTALL.bat
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                    ✅ CÀI ĐẶT HOÀN TẤT!
echo ================================================================================
echo.
echo 📝 CÁC BƯỚC TIẾP THEO:
echo.
echo    1️⃣  Mở file: xiaozhi_endpoints.json
echo    2️⃣  Điền API keys của bạn (Google Gemini / OpenAI)
echo    3️⃣  Save file và đóng lại
echo    4️⃣  Double-click START.bat để khởi động
echo.
echo 📖 Xem hướng dẫn chi tiết trong: README_PORTABLE.txt
echo 📜 Đọc chính sách trong: DISCLAIMER.txt
echo.
echo ================================================================================
echo.
pause
