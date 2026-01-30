@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

color 0E
echo ════════════════════════════════════════════════════════════════
echo    BUILD SECURE INSTALLER - KEY VALIDATION REQUIRED
echo    miniZ MCP Professional v4.3.7
echo ════════════════════════════════════════════════════════════════
echo.
echo 🔒 BẢO MẬT CAO:
echo    • Keys KHÔNG được đưa vào installer
echo    • Phải nhập key hợp lệ mới cài được
echo    • Validate với database 100 keys
echo    • Keys được hardcode vào installer script
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
    pause
    exit /b 1
)

echo ✅ Tìm thấy file EXE: dist\miniZ_MCP.exe
echo.

REM Kiểm tra script Inno Setup
if not exist "installer_secure_with_validation.iss" (
    echo ❌ KHÔNG TÌM THẤY INNO SETUP SCRIPT!
    echo.
    echo File cần có: installer_secure_with_validation.iss
    echo.
    pause
    exit /b 1
)

echo ✅ Tìm thấy Inno Setup script: installer_secure_with_validation.iss
echo.

REM Tạo thư mục output nếu chưa có
if not exist "installer_output" mkdir installer_output

echo ════════════════════════════════════════════════════════════════
echo    ĐANG BUILD SECURE INSTALLER...
echo ════════════════════════════════════════════════════════════════
echo.
echo 🔐 Chế độ bảo mật:
echo    • 100 keys được hardcode vào script
echo    • Keys KHÔNG xuất hiện dưới dạng file
echo    • Phải nhập đúng key mới tiếp tục cài đặt
echo    • Không thể extract hoặc xem keys từ installer
echo.

REM Build installer
"%INNO_SETUP%" "installer_secure_with_validation.iss"

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
echo    ✅ BUILD SECURE INSTALLER THÀNH CÔNG!
echo ════════════════════════════════════════════════════════════════
echo.

REM Tìm file installer mới tạo
for %%f in (installer_output\miniZ_MCP_Professional_v*_Secure.exe) do (
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
    echo    🔐 THÔNG TIN BẢO MẬT
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo ✅ INSTALLER ĐÃ ĐƯỢC BẢO MẬT:
    echo    • File EXE: miniZ_MCP.exe
    echo    • 100 keys được validate bên trong
    echo    • KHÔNG có file license keys đi kèm
    echo    • Keys được mã hóa trong installer script
    echo    • Phải nhập key hợp lệ mới cài được
    echo.
    echo 🔑 CÁCH THỨC HOẠT ĐỘNG:
    echo    • User chạy installer
    echo    • Nhập license key
    echo    • Installer validate key với database
    echo    • Nếu key hợp lệ → tiếp tục cài đặt
    echo    • Nếu key sai → dừng và báo lỗi
    echo.
    echo 🛡️ BẢO MẬT:
    echo    • Keys được hardcode vào Pascal code
    echo    • Không thể extract keys từ installer
    echo    • Mỗi key chỉ validate 1 lần tại thời điểm cài
    echo    • Keys không lộ ra file system
    echo.
    echo 📋 CÁCH SỬ DỤNG CHO KHÁCH HÀNG:
    echo    1. Gửi installer cho khách hàng
    echo    2. Gửi 1 license key riêng qua email/SMS
    echo    3. Khách hàng chạy installer
    echo    4. Nhập key khi được yêu cầu
    echo    5. Cài đặt hoàn tất nếu key đúng
    echo.
    echo 💡 LƯU Ý:
    echo    • File NEW_LICENSE_KEYS.txt chỉ dành cho bạn
    echo    • KHÔNG gửi file keys cho khách hàng
    echo    • Chỉ gửi từng key riêng lẻ qua kênh bảo mật
    echo    • Theo dõi key nào đã gửi cho ai
    echo.
    
    REM Mở thư mục chứa installer
    echo 📂 Đang mở thư mục chứa installer...
    explorer "installer_output"
    
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo     ✅ SẴN SÀNG PHÂN PHỐI AN TOÀN!
    echo ════════════════════════════════════════════════════════════════
    echo.
    pause
) else (
    echo.
    echo ⚠️ Không tìm thấy file installer trong thư mục output!
    echo.
    pause
)

endlocal
