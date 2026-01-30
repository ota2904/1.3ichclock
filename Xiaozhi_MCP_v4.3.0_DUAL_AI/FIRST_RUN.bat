@echo off
REM ============================================================
REM miniZ MCP v4.3.2 - First Run Setup
REM Khởi động lần đầu và cài đặt dependencies
REM ============================================================

cd /d "%~dp0"
color 0B
title miniZ MCP - First Run Setup

echo.
echo ============================================================
echo    miniZ MCP v4.3.2 - FIRST RUN SETUP
echo ============================================================
echo.

REM Kiểm tra xem đã cài dependencies chưa
if exist ".dependencies_installed" (
    echo [OK] Dependencies da duoc cai dat truoc do.
    echo.
    goto :START_APP
)

echo [!] Phat hien chua cai dat dependencies.
echo.
echo Chuong trinh se tu dong cai dat tat ca thu vien can thiet...
echo Qua trinh nay co the mat 2-5 phut.
echo.
echo Nhan phim bat ky de bat dau...
pause >nul

echo.
echo Dang cai dat dependencies...
call AUTO_INSTALL_DEPENDENCIES.bat
if errorlevel 1 (
    echo.
    echo [ERROR] Cai dat khong thanh cong!
    pause
    exit /b 1
)

:START_APP
echo.
echo ============================================================
echo    KHOI DONG miniZ MCP SERVER
echo ============================================================
echo.
echo Dang khoi dong server...
echo.

REM Khởi động server
python xiaozhi_final.py

REM Nếu server tắt, hiển thị thông báo
echo.
echo Server da tat. Nhan phim bat ky de dong...
pause >nul
