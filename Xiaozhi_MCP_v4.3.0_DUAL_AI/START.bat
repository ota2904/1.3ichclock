@echo off
chcp 65001 >nul
title Xiaozhi MCP Control Panel
color 0D

cls
echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║        🚀 XIAOZHI MCP CONTROL PANEL 🚀                  ║
echo ║                   Version 1.0.0                           ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📊 Dashboard: http://localhost:8000
echo 🔌 MCP: Auto-connect with JWT token
echo 🛠️  Tools: 30 available
echo.
echo ═══════════════════════════════════════════════════════════
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python không tìm thấy! Chạy INSTALL.bat trước.
    pause
    exit /b 1
)

:: Khởi động server
echo ⏳ Đang khởi động server...
echo.
python xiaozhi_final.py

:: Nếu server tắt
echo.
echo ═══════════════════════════════════════════════════════════
echo Server đã dừng. Nhấn phím bất kỳ để thoát...
pause >nul
