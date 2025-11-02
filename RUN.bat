@echo off
chcp 65001 >nul
color 0A
title Xiaozhi Ultimate Server - 1 Click Start

cls
echo.
echo ============================================================
echo    🚀 XIAOZHI ULTIMATE SERVER
echo ============================================================
echo.
echo    ✨ All-in-One: Web UI + WebSocket MCP + Dashboard
echo    🌐 URL: http://localhost:8000
echo    📡 Xiaozhi MCP: Auto-connect
echo    🛑 Nhấn Ctrl+C để dừng
echo.
echo ============================================================
echo.
echo    Đang khởi động server...
echo.

python xiaozhi_ultimate.py

echo.
echo    Server đã dừng. Nhấn phím bất kỳ để thoát...
pause >nul
