@echo off
chcp 65001 >nul
title 🏗️ miniZ MCP - Professional Installer Builder (Customer Edition)
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║     🏗️  miniZ MCP Professional Installer Builder        ║
echo ║              Customer Edition - Full Features            ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

REM ============================================================
REM STEP 1: Check Inno Setup
REM ============================================================
echo [1/5] Kiểm tra Inno Setup Compiler...
echo ------------------------------------------------------------
echo.

set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6"
set "INNO_COMPILER=%INNO_PATH%\ISCC.exe"

if not exist "%INNO_COMPILER%" (
    echo ❌ Không tìm thấy Inno Setup!
    echo.
    echo 📥 Vui lòng tải và cài đặt Inno Setup:
    echo    https://jrsoftware.org/isdl.php
    echo.
    echo Sau khi cài đặt, chạy lại script này.
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy Inno Setup!

echo.
echo ------------------------------------------------------------
echo.

REM ============================================================
REM STEP 2: Check Required Files
REM ============================================================
echo [2/5] Kiểm tra files cần thiết...
echo ------------------------------------------------------------
echo.

set MISSING=0

if not exist "xiaozhi_final.py" (
    echo ❌ Thiếu: xiaozhi_final.py
    set MISSING=1
) else (
    echo ✅ xiaozhi_final.py
)

if not exist "requirements.txt" (
    echo ❌ Thiếu: requirements.txt
    set MISSING=1
) else (
    echo ✅ requirements.txt
)

if not exist "START.bat" (
    echo ❌ Thiếu: START.bat
    set MISSING=1
) else (
    echo ✅ START.bat
)

if not exist "installer_professional.iss" (
    echo ❌ Thiếu: installer_professional.iss
    set MISSING=1
) else (
    echo ✅ installer_professional.iss
)

REM Check optional files
if exist "icon.ico" (
    echo ✅ icon.ico (Optional)
) else (
    echo ⚠️  icon.ico không có - sẽ dùng icon mặc định
)

if exist "music_library\" (
    echo ✅ music_library\
) else (
    echo ⚠️  music_library\ không có - sẽ bỏ qua
)

if %MISSING%==1 (
    echo.
    echo ❌ Thiếu files cần thiết! Không thể build installer.
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Tất cả files bắt buộc đã sẵn sàng!

REM ============================================================
REM STEP 3: Create Output Directory
REM ============================================================
echo.
echo [3/5] Tạo thư mục output...
echo ------------------------------------------------------------
echo.

if not exist "installer_output" (
    mkdir installer_output
    echo ✅ Đã tạo: installer_output\
) else (
    echo ℹ️  Thư mục installer_output đã tồn tại
)

echo.
echo ------------------------------------------------------------
echo.

REM ============================================================
REM STEP 4: Build with Inno Setup
REM ============================================================
echo [4/5] Build installer với Inno Setup...
echo ------------------------------------------------------------
echo.

echo 🔨 Compiling installer_professional.iss...
echo.

"%INNO_COMPILER%" installer_professional.iss

if errorlevel 1 (
    echo.
    echo ❌ Build thất bại!
    echo.
    echo Lỗi có thể do:
    echo   • Sai cú pháp trong installer_professional.iss
    echo   • Thiếu files được reference trong script
    echo   • Quyền admin không đủ
    echo   • Đường dẫn Inno Setup không đúng
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ Compilation thành công!

REM ============================================================
REM STEP 5: Verify Output
REM ============================================================
echo.
echo [5/5] Kiểm tra installer đã build...
echo ------------------------------------------------------------
echo.

if exist "installer_output\miniZ_MCP_Professional_Setup_v4.3.0.exe" (
    echo ✅ Tìm thấy installer!
    echo.
    echo 📦 File: installer_output\miniZ_MCP_Professional_Setup_v4.3.0.exe
    
    REM Get file size
    for %%F in ("installer_output\miniZ_MCP_Professional_Setup_v4.3.0.exe") do (
        set size=%%~zF
        set /a size_mb=!size! / 1048576
        echo 💾 Kích thước: !size_mb! MB
    )
    
    echo.
    echo ╔════════════════════════════════════════════════════════════════╗
    echo ║           ✅ BUILD INSTALLER THÀNH CÔNG!                      ║
    echo ╚════════════════════════════════════════════════════════════════╝
    echo.
    echo ✨ TÍNH NĂNG INSTALLER:
    echo    • Tự động phát hiện Python hoặc tải về Python 3.11.9
    echo    • Cài đặt tự động tất cả thư viện (pip install -r requirements.txt)
    echo    • Khởi động cùng Windows (Registry HKCU\Run)
    echo    • Desktop + Start Menu shortcuts
    echo    • Giao diện chuyên nghiệp với tiếng Việt
    echo    • Uninstaller với tùy chọn giữ lại dữ liệu
    echo    • Component-based installation (chọn tính năng cài đặt)
    echo    • Tự động mở Dashboard sau khi cài
    echo.
    echo 📦 CÀI ĐẶT CHO KHÁCH HÀNG:
    echo    1. Gửi file: miniZ_MCP_Professional_Setup_v4.3.0.exe
    echo    2. Double-click để chạy installer
    echo    3. Chọn "Cài đặt đầy đủ" (Recommended)
    echo    4. Chọn thư mục cài đặt
    echo    5. Chọn tính năng: Desktop icon, Auto-startup, Start after install
    echo    6. Click "Install" và đợi
    echo    7. Python sẽ tự động tải và cài (nếu chưa có)
    echo    8. Thư viện sẽ tự động cài
    echo    9. Dashboard tự động mở: http://localhost:8000
    echo.
    echo 🔧 YÊU CẦU HỆ THỐNG:
    echo    • Windows 10/11 (Build 17763 trở lên)
    echo    • 500 MB dung lượng trống
    echo    • Quyền Administrator
    echo    • Internet (để tải Python nếu chưa có)
    echo.
    echo 📁 CẤU TRÚC SAU KHI CÀI:
    echo    • Program Files\miniZ_MCP\ - Ứng dụng chính
    echo    • Desktop\ - Shortcut miniZ MCP Professional
    echo    • Start Menu\miniZ MCP Professional\ - Program group
    echo    • %%LOCALAPPDATA%%\miniZ_MCP\ - Dữ liệu người dùng
    echo    • Registry HKCU\Run - Auto-startup
    echo.
    echo ═══════════════════════════════════════════════════════════════════
    echo.
    
    REM Open output folder
    echo 📁 Đang mở thư mục output...
    explorer installer_output
    
) else (
    echo ❌ Không tìm thấy file installer!
    echo.
    echo Kiểm tra:
    echo   • Inno Setup đã build thành công chưa?
    echo   • OutputDir trong installer_professional.iss đúng chưa?
    echo   • OutputBaseFilename có đúng không?
    echo.
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════════
echo 🎉 HOÀN TẤT! Customer installer đã sẵn sàng để phân phối.
echo ═══════════════════════════════════════════════════════════════════
echo.
pause
