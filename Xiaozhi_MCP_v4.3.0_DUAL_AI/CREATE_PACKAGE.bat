@echo off
chcp 65001 >nul
title 📦 Tạo Package Portable - Xiaozhi MCP v4.3.0

echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║        📦 TẠO PACKAGE PORTABLE - XIAOZHI MCP v4.3.0          ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

echo 🔄 Đang chuẩn bị package...
timeout /t 2 >nul

REM Kiểm tra 7-Zip
set SEVENZIP="C:\Program Files\7-Zip\7z.exe"
if not exist %SEVENZIP% (
    set SEVENZIP="C:\Program Files (x86)\7-Zip\7z.exe"
)

if not exist %SEVENZIP% (
    echo ❌ Không tìm thấy 7-Zip!
    echo.
    echo 📥 Vui lòng cài đặt 7-Zip từ: https://www.7-zip.org/
    echo.
    pause
    exit /b
)

REM Tạo tên file zip
set TIMESTAMP=%date:~6,4%%date:~3,2%%date:~0,2%
set ZIPNAME=Xiaozhi_MCP_v4.3.0_PORTABLE_%TIMESTAMP%.zip

echo.
echo 📂 Tên package: %ZIPNAME%
echo.

REM Xóa xiaozhi_endpoints.json nếu có (không đóng gói token thật)
if exist "xiaozhi_endpoints.json" (
    echo ⚠️  Đang xóa xiaozhi_endpoints.json (bảo mật)...
    del /f /q "xiaozhi_endpoints.json" >nul 2>&1
)

REM Copy template thành file chính
if exist "xiaozhi_endpoints_template.json" (
    echo ✅ Sử dụng file template (không chứa token)
    copy /y "xiaozhi_endpoints_template.json" "xiaozhi_endpoints.json" >nul
)

echo.
echo 🗜️  Đang nén các file...
echo.

REM Tạo file zip với tất cả nội dung
%SEVENZIP% a -tzip "%ZIPNAME%" ^
    "xiaozhi_final.py" ^
    "requirements.txt" ^
    "xiaozhi_endpoints.json" ^
    "README.md" ^
    "PORTABLE_README.md" ^
    "PACKAGE_README.txt" ^
    "DISCLAIMER.md" ^
    "LICENSE" ^
    "CHANGELOG.md" ^
    "QUICKSTART.md" ^
    "MUSIC_GUIDE.md" ^
    "GEMINI_GUIDE.md" ^
    "GPT4_GUIDE.md" ^
    "HUONG_DAN_THONG_TIN_MOI.md" ^
    "DUAL_AI_SUMMARY.txt" ^
    "INSTALL.bat" ^
    "START.bat" ^
    "CHECK.bat" ^
    "CREATE_SHORTCUT.bat" ^
    "TEST_GEMINI.bat" ^
    "music_library\" ^
    -mx=9 >nul

if %errorlevel% equ 0 (
    echo.
    echo ╔═══════════════════════════════════════════════════════════════╗
    echo ║                                                               ║
    echo ║        ✅ TẠO PACKAGE THÀNH CÔNG!                            ║
    echo ║                                                               ║
    echo ╚═══════════════════════════════════════════════════════════════╝
    echo.
    echo 📦 File: %ZIPNAME%
    echo 📂 Thư mục hiện tại: %cd%
    echo.
    echo 📋 Package bao gồm:
    echo    ✅ Phần mềm hoàn chỉnh (xiaozhi_final.py)
    echo    ✅ Tài liệu đầy đủ (README, DISCLAIMER, GUIDES)
    echo    ✅ Script cài đặt (INSTALL.bat, START.bat)
    echo    ✅ Thư viện nhạc (music_library)
    echo    ✅ Template cấu hình (không chứa token)
    echo.
    echo 🔒 BẢO MẬT:
    echo    ✅ Đã xóa token/API keys thật
    echo    ✅ Sử dụng file template trống
    echo    ✅ An toàn để giao khách hàng
    echo.
    echo 🎁 READY TO DELIVER!
    echo.
    
    REM Mở thư mục chứa file zip
    explorer /select,"%cd%\%ZIPNAME%"
) else (
    echo.
    echo ❌ Lỗi khi tạo package!
    echo.
)

echo.
pause
