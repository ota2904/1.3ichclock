@echo off
chcp 65001 >nul
title Kiểm Tra Môi Trường
color 0E

echo.
echo ═══════════════════════════════════════════════════════════
echo    KIỂM TRA MÔI TRƯỜNG - XIAOZHI MCP
echo ═══════════════════════════════════════════════════════════
echo.

:: Kiểm tra Python
echo [1/3] Kiểm tra Python...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python chưa cài đặt hoặc chưa thêm vào PATH
    echo    → Tải Python từ: https://python.org
    echo    → Nhớ tích "Add Python to PATH" khi cài
    goto :error
) else (
    for /f "tokens=2" %%i in ('python --version') do echo ✅ Python %%i
)
echo.

:: Kiểm tra pip
echo [2/3] Kiểm tra pip...
pip --version 2>nul
if %errorlevel% neq 0 (
    echo ❌ pip chưa có
    goto :error
) else (
    echo ✅ pip sẵn sàng
)
echo.

:: Kiểm tra thư viện
echo [3/3] Kiểm tra thư viện Python...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Thư viện chưa cài - Chạy INSTALL.bat để cài đặt
) else (
    echo ✅ FastAPI: OK
)

python -c "import uvicorn" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  Uvicorn chưa cài
) else (
    echo ✅ Uvicorn: OK
)

python -c "import psutil" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  psutil chưa cài
) else (
    echo ✅ psutil: OK
)

python -c "import websockets" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  websockets chưa cài
) else (
    echo ✅ websockets: OK
)

python -c "import pyautogui" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  pyautogui chưa cài
) else (
    echo ✅ pyautogui: OK
)

python -c "import pyperclip" 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  pyperclip chưa cài
) else (
    echo ✅ pyperclip: OK
)

echo.
echo ═══════════════════════════════════════════════════════════
echo    ✅ KIỂM TRA HOÀN TẤT!
echo ═══════════════════════════════════════════════════════════
echo.
echo 📋 Tổng kết:
echo    - Nếu thấy ⚠️  → Chạy INSTALL.bat để cài đặt
echo    - Nếu tất cả ✅ → Chạy START.bat để khởi động
echo.
goto :end

:error
echo.
echo ═══════════════════════════════════════════════════════════
echo    ❌ PHÁT HIỆN VẤN ĐỀ!
echo ═══════════════════════════════════════════════════════════
echo.
echo 🔧 Giải pháp:
echo    1. Cài Python 3.13+ từ https://python.org
echo    2. Khởi động lại máy tính
echo    3. Chạy lại CHECK.bat
echo.

:end
pause
