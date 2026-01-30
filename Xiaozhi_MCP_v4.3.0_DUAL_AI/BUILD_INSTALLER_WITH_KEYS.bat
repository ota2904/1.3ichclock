@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0A
echo ════════════════════════════════════════════════════════════════
echo    BUILD INSTALLER WITH LICENSE KEYS BATCH
echo    miniZ MCP Professional v4.3.7
echo ════════════════════════════════════════════════════════════════
echo.

REM Kiểm tra Inno Setup
set "INNO_SETUP=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_SETUP%" (
    echo ❌ KHÔNG TÌM THẤY INNO SETUP!
    echo.
    echo Vui lòng cài đặt Inno Setup 6:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy Inno Setup: %INNO_SETUP%
echo.

REM Kiểm tra file EXE
if not exist "dist\miniZ_MCP.exe" (
    echo ❌ KHÔNG TÌM THẤY FILE EXE!
    echo.
    echo File cần có: dist\miniZ_MCP.exe
    echo.
    echo Vui lòng build EXE trước khi tạo installer.
    pause
    exit /b 1
)

echo ✅ Tìm thấy file EXE: dist\miniZ_MCP.exe
echo.

REM Kiểm tra file license keys
if not exist "NEW_LICENSE_KEYS.txt" (
    echo ❌ KHÔNG TÌM THẤY FILE LICENSE KEYS!
    echo.
    echo File cần có: NEW_LICENSE_KEYS.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy file license keys: NEW_LICENSE_KEYS.txt
echo.

REM Kiểm tra script Inno Setup
if not exist "installer_with_keys_batch.iss" (
    echo ❌ KHÔNG TÌM THẤY INNO SETUP SCRIPT!
    echo.
    echo File cần có: installer_with_keys_batch.iss
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy Inno Setup script: installer_with_keys_batch.iss
echo.

REM Tạo thư mục output nếu chưa có
if not exist "installer_output" mkdir installer_output

echo ════════════════════════════════════════════════════════════════
echo    ĐANG BUILD INSTALLER...
echo ════════════════════════════════════════════════════════════════
echo.

REM Build installer
"%INNO_SETUP%" "installer_with_keys_batch.iss"

if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo    ❌ BUILD INSTALLER THẤT BẠI!
    echo ════════════════════════════════════════════════════════════════
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════════════
echo    ✅ BUILD INSTALLER THÀNH CÔNG!
echo ════════════════════════════════════════════════════════════════
echo.

REM Tìm file installer mới tạo
for %%f in (installer_output\miniZ_MCP_Professional_v*.exe) do (
    set "INSTALLER_FILE=%%f"
)

if defined INSTALLER_FILE (
    echo 📦 File installer: !INSTALLER_FILE!
    
    REM Hiển thị thông tin file
    for %%A in ("!INSTALLER_FILE!") do (
        set "FILE_SIZE=%%~zA"
        set "FILE_DATE=%%~tA"
    )
    
    REM Chuyển đổi kích thước sang MB
    set /a "SIZE_MB=!FILE_SIZE! / 1048576"
    
    echo 📊 Kích thước: !SIZE_MB! MB
    echo 📅 Ngày tạo: !FILE_DATE!
    echo.
    
    echo ════════════════════════════════════════════════════════════════
    echo    📋 THÔNG TIN INSTALLER
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo ✨ Installer đã được tích hợp:
    echo    • File EXE: miniZ_MCP.exe
    echo    • 100 License Keys Professional
    echo    • File: NEW_LICENSE_KEYS.txt
    echo    • Hướng dẫn kích hoạt chi tiết
    echo    • Tự động tạo shortcuts
    echo.
    echo 🔑 LICENSE KEYS:
    echo    • Loại: Professional (Vô thời hạn)
    echo    • Số lượng: 100 keys
    echo    • 1 key = 1 máy tính
    echo    • Định dạng: XXXX-XXXX-XXXX-XXXX
    echo.
    echo 💡 HƯỚNG DẪN SỬ DỤNG:
    echo    1. Chạy file installer
    echo    2. Làm theo hướng dẫn cài đặt
    echo    3. Sau khi cài đặt, mở file NEW_LICENSE_KEYS.txt
    echo    4. Chọn 1 license key bất kỳ
    echo    5. Khởi động ứng dụng và nhập key để kích hoạt
    echo.
    
    REM Mở thư mục chứa installer
    echo 📂 Đang mở thư mục chứa installer...
    explorer "installer_output"
    
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo Press any key to exit...
    pause >nul
) else (
    echo.
    echo ⚠️ Không tìm thấy file installer trong thư mục output!
    echo.
    pause
)

endlocal
