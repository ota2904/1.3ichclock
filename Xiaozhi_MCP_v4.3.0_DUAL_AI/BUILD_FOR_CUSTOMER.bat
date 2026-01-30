@echo off
chcp 65001 >nul
title 🚀 miniZ MCP - Build EXE cho Khách Hàng

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║    🚀 miniZ MCP - Build EXE Professional v4.3.0          ║
echo ╠══════════════════════════════════════════════════════════╣
echo ║  Tạo file cài đặt cho khách hàng:                        ║
echo ║  ✅ Không lộ API keys                                    ║
echo ║  ✅ Mã hóa thông tin nhạy cảm                            ║
echo ║  ✅ Bao gồm INSTALL.bat và UNINSTALL.bat                 ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo    Vui lòng cài Python từ python.org
    pause
    exit /b 1
)

echo 📦 Cài đặt dependencies...
pip install pyinstaller pystray Pillow --quiet --upgrade

echo.
echo 🔨 Bắt đầu build...
echo.

python build_exe_pro.py

echo.
if errorlevel 1 (
    echo ❌ Build thất bại! Kiểm tra lỗi ở trên.
) else (
    echo ✅ Build hoàn tất! File output trong thư mục "output"
)

echo.
echo 👋 Nhấn phím bất kỳ để đóng...
pause >nul
