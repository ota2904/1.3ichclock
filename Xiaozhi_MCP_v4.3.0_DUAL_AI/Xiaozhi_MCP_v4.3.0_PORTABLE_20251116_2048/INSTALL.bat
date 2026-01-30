@echo off
chcp 65001 >nul
title Xiaozhi MCP - Cài Đặt Tự Động
color 0B

echo.
echo ═══════════════════════════════════════════════════════════
echo    XIAOZHI MCP CONTROL PANEL - TỰ ĐỘNG CÀI ĐẶT
echo ═══════════════════════════════════════════════════════════
echo.

:: Kiểm tra Python
echo [1/4] Kiểm tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Chưa cài Python! Vui lòng cài Python 3.13+ từ https://python.org
    pause
    exit /b 1
)
echo ✅ Python đã có sẵn
echo.

:: Kiểm tra pip
echo [2/4] Kiểm tra pip...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Pip chưa có! Đang cài đặt...
    python -m ensurepip --upgrade
)
echo ✅ Pip sẵn sàng
echo.

:: Cài đặt dependencies
echo [3/4] Đang cài đặt thư viện...
echo    • FastAPI, Uvicorn (Web framework)
echo    • psutil (System monitoring)
echo    • websockets (MCP connection)
echo    • pyautogui, pyperclip (Automation)
echo.
pip install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo ❌ Lỗi khi cài đặt! Thử lại với:
    echo    pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✅ Đã cài đặt xong tất cả thư viện
echo.

:: Hoàn tất
echo [4/4] Kiểm tra cấu hình...
python -c "import fastapi, uvicorn, psutil, websockets, pyautogui, pyperclip; print('✅ Tất cả thư viện hoạt động tốt!')"
echo.

echo ═══════════════════════════════════════════════════════════
echo    🎉 CÀI ĐẶT THÀNH CÔNG!
echo ═══════════════════════════════════════════════════════════
echo.
echo 📋 Bước tiếp theo:
echo    1. Lấy JWT token từ https://dash.upx8.com
echo    2. Chạy START.bat để khởi động server
echo    3. Mở http://localhost:8000 trong trình duyệt
echo    4. Dán JWT token vào tab "Cấu hình"
echo.
echo 🚀 Nhấn phím bất kỳ để khởi động ngay...
pause >nul
START.bat
