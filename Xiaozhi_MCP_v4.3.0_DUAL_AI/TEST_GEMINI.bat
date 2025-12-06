@echo off
chcp 65001 >nul
title Test Gemini AI Integration
color 0E

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║        🧪 TEST GEMINI AI INTEGRATION 🧪                  ║
echo ║                   Xiaozhi MCP                             ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: Kiểm tra Python
echo 📦 Kiểm tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python không tìm thấy!
    echo    Vui lòng cài Python từ https://python.org
    pause
    exit /b 1
)
echo ✅ Python OK
echo.

:: Kiểm tra google-generativeai
echo 📦 Kiểm tra google-generativeai...
python -c "import google.generativeai" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  google-generativeai chưa cài đặt
    echo.
    echo 📥 Đang cài đặt google-generativeai...
    pip install google-generativeai --quiet
    if %errorlevel% neq 0 (
        echo ❌ Cài đặt thất bại!
        pause
        exit /b 1
    )
    echo ✅ Đã cài đặt google-generativeai
)
echo ✅ google-generativeai OK
echo.

:: Chạy test
echo ═══════════════════════════════════════════════════════════
echo.
python test_gemini.py

:: Pause để xem kết quả
echo.
echo ═══════════════════════════════════════════════════════════
echo Nhấn phím bất kỳ để thoát...
pause >nul

