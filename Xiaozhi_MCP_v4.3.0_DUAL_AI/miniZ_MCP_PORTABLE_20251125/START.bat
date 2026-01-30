@echo off
chcp 65001 >nul
title miniZ MCP - KHỞI ĐỘNG
color 0B

echo ================================================================================
echo                    🌳 miniZ MCP v4.3.0 - KHỞI ĐỘNG
echo ================================================================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ LỖI: Python chưa được cài đặt!
    echo.
    echo Vui lòng chạy INSTALL.bat trước
    echo.
    pause
    exit /b 1
)

REM Kiểm tra xiaozhi_final.py
if not exist "xiaozhi_final.py" (
    color 0C
    echo ❌ LỖI: Không tìm thấy file xiaozhi_final.py!
    echo.
    echo Vui lòng chạy file START.bat từ đúng thư mục miniZ_MCP
    echo.
    pause
    exit /b 1
)

REM Kiểm tra file cấu hình API
if not exist "xiaozhi_endpoints.json" (
    color 0E
    echo ⚠️  CẢNH BÁO: Không tìm thấy file xiaozhi_endpoints.json!
    echo.
    echo File này cần thiết để cấu hình API keys.
    echo Phần mềm sẽ không hoạt động nếu chưa có API keys.
    echo.
    echo Vui lòng tạo file xiaozhi_endpoints.json theo hướng dẫn
    echo trong README_PORTABLE.txt
    echo.
    pause
)

echo ✅ Đang kiểm tra dependencies...
echo.

REM Kiểm tra một số packages quan trọng
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    color 0E
    echo ⚠️  CẢNH BÁO: Thiếu Python packages!
    echo.
    echo Vui lòng chạy INSTALL.bat trước khi khởi động
    echo.
    pause
    exit /b 1
)

echo ✅ Dependencies OK
echo.
echo ================================================================================
echo                    🚀 ĐANG KHỞI ĐỘNG miniZ MCP...
echo ================================================================================
echo.
echo 📡 Web Dashboard sẽ tự động mở tại: http://localhost:8000
echo 🌐 Nếu không tự mở, hãy mở browser và truy cập URL trên
echo.
echo ⚠️  Để DỪNG server: Nhấn Ctrl+C trong cửa sổ này
echo.
echo ================================================================================
echo.

REM Khởi động server
python xiaozhi_final.py

REM Nếu có lỗi
if %errorlevel% neq 0 (
    echo.
    color 0C
    echo ================================================================================
    echo                    ❌ PHẦN MỀM DỪNG VỚI LỖI!
    echo ================================================================================
    echo.
    echo 🔧 CÁC BƯỚC KHẮC PHỤC:
    echo.
    echo    1. Kiểm tra file xiaozhi_endpoints.json đã điền đúng API keys chưa
    echo    2. Kiểm tra port 8000 có đang được dùng không
    echo    3. Chạy lại INSTALL.bat
    echo    4. Xem chi tiết lỗi phía trên
    echo.
    echo 📖 Xem hướng dẫn xử lý lỗi trong: README_PORTABLE.txt (mục 7)
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo                    👋 CẢM ƠN BẠN ĐÃ SỬ DỤNG miniZ MCP!
echo ================================================================================
echo.
pause
