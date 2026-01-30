@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════════
echo     🔍 KIỂM TRA AUTO-START WINDOWS - miniZ MCP v4.3.0
echo ═══════════════════════════════════════════════════════════════
echo.

echo [1/3] Kiểm tra Registry entry...
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ Registry entry TỒN TẠI
    echo.
    echo     📋 Chi tiết:
    reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP"
) else (
    echo     ❌ Registry entry KHÔNG TỒN TẠI
    echo.
    echo     ⚠️  Auto-start chưa được kích hoạt.
    echo     💡 Cách kích hoạt:
    echo        1. Gỡ cài đặt miniZ MCP
    echo        2. Cài đặt lại và TÍCHchọn "🚀 Tự động khởi động cùng Windows"
    echo.
)

echo.
echo [2/3] Kiểm tra file START_HIDDEN.bat...
if exist "%~dp0START_HIDDEN.bat" (
    echo     ✅ File START_HIDDEN.bat TỒN TẠI
) else (
    echo     ❌ File START_HIDDEN.bat KHÔNG TỒN TẠI
    echo        ⚠️  File khởi động bị thiếu!
)

echo.
echo [3/3] Kiểm tra đường dẫn Registry...
for /f "tokens=2*" %%a in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP" 2^>nul ^| find "miniZ_MCP"') do (
    set REGPATH=%%b
)
if defined REGPATH (
    echo     📂 Đường dẫn trong Registry:
    echo        %REGPATH%
    echo.
    if exist "%REGPATH%" (
        echo     ✅ File được trỏ tới TỒN TẠI
    ) else (
        echo     ❌ File được trỏ tới KHÔNG TỒN TẠI
        echo        ⚠️  Đường dẫn không hợp lệ!
    )
) else (
    echo     ⚠️  Không tìm thấy đường dẫn (Registry entry không tồn tại)
)

echo.
echo ═══════════════════════════════════════════════════════════════
echo                         KẾT LUẬN
echo ═══════════════════════════════════════════════════════════════

reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP" >nul 2>&1
if %errorlevel% equ 0 (
    echo     ✅ AUTO-START: HOẠT ĐỘNG
    echo     🚀 miniZ MCP sẽ tự động khởi động khi Windows bật
) else (
    echo     ❌ AUTO-START: CHƯA KÍCH HOẠT
    echo     💡 Chạy lệnh sau để KÍCH HOẠT AUTO-START:
    echo.
    echo        reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "miniZ_MCP" /t REG_SZ /d "%~dp0START_HIDDEN.bat" /f
    echo.
)

echo ═══════════════════════════════════════════════════════════════
echo.
pause
