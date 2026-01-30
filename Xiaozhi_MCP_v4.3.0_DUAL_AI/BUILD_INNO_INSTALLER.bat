@echo off
chcp 65001 > nul
title miniZ MCP - Professional Installer Builder
color 0A

echo ╔══════════════════════════════════════════════════════════════╗
echo ║     miniZ MCP v4.3.0 - PROFESSIONAL INSTALLER BUILDER        ║
echo ║                    Powered by Inno Setup                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: Check Inno Setup installation
set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
) else (
    echo ❌ KHÔNG TÌM THẤY INNO SETUP 6!
    echo.
    echo Vui lòng tải và cài đặt Inno Setup 6 từ:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo Hoặc chạy lệnh: winget install JRSoftware.InnoSetup
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy Inno Setup: %ISCC%
echo.

:: Check required files
echo [1/4] Kiểm tra các file cần thiết...

set MISSING=0

if not exist "xiaozhi_final.py" (
    echo ❌ Thiếu: xiaozhi_final.py
    set MISSING=1
)
if not exist "LICENSE_VI.txt" (
    echo ❌ Thiếu: LICENSE_VI.txt
    set MISSING=1
)
if not exist "logo.ico" (
    echo ⚠️  Cảnh báo: logo.ico không tìm thấy
    echo    Sẽ sử dụng icon mặc định
)
if not exist "START.bat" (
    echo ❌ Thiếu: START.bat
    set MISSING=1
)
if not exist "requirements.txt" (
    echo ❌ Thiếu: requirements.txt
    set MISSING=1
)

if %MISSING%==1 (
    echo.
    echo ❌ Thiếu các file cần thiết. Vui lòng kiểm tra lại!
    pause
    exit /b 1
)

echo ✅ Tất cả file cần thiết đã sẵn sàng
echo.

:: Create README_INSTALL.txt if not exists
if not exist "README_INSTALL.txt" (
    echo [2/4] Tạo file README_INSTALL.txt...
    (
        echo ╔══════════════════════════════════════════════════════════════╗
        echo ║           CHÀO MỪNG ĐẾN VỚI miniZ MCP v4.3.0                 ║
        echo ║              Professional AI Assistant                        ║
        echo ╚══════════════════════════════════════════════════════════════╝
        echo.
        echo ▶ GIỚI THIỆU:
        echo.
        echo   miniZ MCP là hệ thống MCP Server tiên tiến, tích hợp AI để
        echo   hỗ trợ công việc hàng ngày. Với khả năng:
        echo.
        echo   • Tìm kiếm thông tin thông minh ^(Google, DuckDuckGo^)
        echo   • Điều khiển nhạc VLC
        echo   • Quản lý file và thư mục
        echo   • Tích hợp đa thiết bị Xiaozhi
        echo   • Hỗ trợ Gemini AI và GPT-4
        echo.
        echo ▶ YÊU CẦU HỆ THỐNG:
        echo.
        echo   • Windows 10/11 ^(64-bit^)
        echo   • Python 3.10 trở lên
        echo   • 4GB RAM tối thiểu
        echo   • Kết nối Internet
        echo.
        echo ▶ SAU KHI CÀI ĐẶT:
        echo.
        echo   1. Chạy INSTALL.bat để cài đặt dependencies
        echo   2. Cấu hình API keys trong xiaozhi_endpoints.json
        echo   3. Chạy START.bat để khởi động server
        echo   4. Truy cập http://localhost:8000
        echo.
        echo ════════════════════════════════════════════════════════════════
    ) > README_INSTALL.txt
    echo ✅ Đã tạo README_INSTALL.txt
) else (
    echo [2/4] README_INSTALL.txt đã tồn tại
)

:: Create POST_INSTALL_INFO.txt if not exists
if not exist "POST_INSTALL_INFO.txt" (
    echo [3/4] Tạo file POST_INSTALL_INFO.txt...
    (
        echo ╔══════════════════════════════════════════════════════════════╗
        echo ║         CÀI ĐẶT THÀNH CÔNG - miniZ MCP v4.3.0                ║
        echo ╚══════════════════════════════════════════════════════════════╝
        echo.
        echo ✅ HOÀN THÀNH CÀI ĐẶT!
        echo.
        echo ▶ BƯỚC TIẾP THEO:
        echo.
        echo   1. Mở thư mục cài đặt
        echo   2. Chạy INSTALL.bat ^(lần đầu tiên^)
        echo   3. Đợi cài đặt Python dependencies hoàn tất
        echo   4. Chạy START.bat để khởi động
        echo.
        echo ▶ CẤU HÌNH API KEYS:
        echo.
        echo   Mở file xiaozhi_endpoints.json và thêm:
        echo   • Gemini API Key ^(khuyến nghị^)
        echo   • OpenAI API Key ^(tùy chọn^)
        echo   • Serper API Key ^(cho tìm kiếm Google^)
        echo.
        echo ▶ HỖ TRỢ:
        echo.
        echo   • Xem QUICKSTART.md để bắt đầu nhanh
        echo   • Xem GEMINI_GUIDE.md cho Gemini AI
        echo   • Xem GPT4_GUIDE.md cho OpenAI GPT-4
        echo.
        echo ▶ WEB DASHBOARD:
        echo.
        echo   Sau khi khởi động, truy cập:
        echo   http://localhost:8000
        echo.
        echo ════════════════════════════════════════════════════════════════
        echo           Cảm ơn bạn đã sử dụng miniZ MCP!
        echo ════════════════════════════════════════════════════════════════
    ) > POST_INSTALL_INFO.txt
    echo ✅ Đã tạo POST_INSTALL_INFO.txt
) else (
    echo [3/4] POST_INSTALL_INFO.txt đã tồn tại
)

:: Create output directory
if not exist "installer_output" mkdir installer_output

:: Build installer
echo.
echo [4/4] Đang build installer...
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    BUILDING INSTALLER                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

"%ISCC%" "miniZ_Professional_Setup.iss"

if %ERRORLEVEL%==0 (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║               ✅ BUILD THÀNH CÔNG!                           ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo 📦 Installer đã được tạo tại:
    echo    installer_output\miniZ_MCP_v4.3.0_Professional_Setup.exe
    echo.
    echo 📋 Bạn có thể giao file này cho khách hàng để cài đặt.
    echo.
    
    :: Open output folder
    start "" "installer_output"
) else (
    echo.
    echo ╔══════════════════════════════════════════════════════════════╗
    echo ║               ❌ BUILD THẤT BẠI!                             ║
    echo ╚══════════════════════════════════════════════════════════════╝
    echo.
    echo Vui lòng kiểm tra lỗi ở trên và thử lại.
)

echo.
pause
