@echo off
chcp 65001 >nul
color 0A
title miniZ MCP - Kiểm Tra Tương Thích Hệ Thống

echo.
echo ═══════════════════════════════════════════════════════════════════
echo     miniZ MCP v4.3.0 - Kiểm Tra Tương Thích
echo ═══════════════════════════════════════════════════════════════════
echo.

REM Check Windows Version
echo [1/5] Kiểm tra phiên bản Windows...
ver | findstr /i "10.0" >nul
if %errorlevel% == 0 (
    echo ✅ Windows 10/11 detected - COMPATIBLE
) else (
    echo ❌ Yêu cầu Windows 10/11 trở lên
    set COMPATIBLE=NO
)
echo.

REM Check 64-bit
echo [2/5] Kiểm tra kiến trúc CPU...
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    echo ✅ 64-bit architecture detected - COMPATIBLE
) else (
    echo ❌ Yêu cầu Windows 64-bit
    set COMPATIBLE=NO
)
echo.

REM Check RAM
echo [3/5] Kiểm tra RAM...
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| findstr /C:"Total Physical Memory"') do set RAM=%%a
echo    RAM: %RAM%
echo ✅ RAM check passed
echo.

REM Check Disk Space
echo [4/5] Kiểm tra dung lượng ổ đĩa...
for /f "tokens=3" %%a in ('dir /-c %systemdrive%\ ^| find "bytes free"') do set FREE_SPACE=%%a
echo    Free space: %FREE_SPACE% bytes
echo ✅ Disk space check passed
echo.

REM Check Admin Rights
echo [5/5] Kiểm tra quyền Admin...
net session >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Running with Admin privileges
) else (
    echo ⚠️  Không có quyền Admin (cần cho lần cài đầu)
    echo    Tip: Right-click và chọn "Run as administrator"
)
echo.

echo ═══════════════════════════════════════════════════════════════════
echo.

if not "%COMPATIBLE%"=="NO" (
    echo ✅ HỆ THỐNG TƯƠNG THÍCH!
    echo.
    echo miniZ MCP có thể chạy trên máy tính này.
    echo.
) else (
    echo ❌ HỆ THỐNG KHÔNG TƯƠNG THÍCH
    echo.
    echo Vui lòng nâng cấp lên:
    echo - Windows 10/11 64-bit
    echo.
)

echo Chi tiết hệ thống:
echo ───────────────────────────────────────────────────────────────────
systeminfo | findstr /C:"OS Name" /C:"OS Version" /C:"System Type" /C:"Processor"
echo.

echo ═══════════════════════════════════════════════════════════════════
echo.
pause
