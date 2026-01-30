@echo off
chcp 65001 >nul
color 0A
title TEST LICENSE SYSTEM - miniZ MCP Professional v4.3.0

echo ============================================================
echo 🔐 TEST LICENSE SYSTEM - miniZ_MCP_Professional.exe
echo ============================================================
echo.

echo [INFO] File EXE Location:
echo %CD%\dist\miniZ_MCP_Professional.exe
echo.

echo [INFO] File Size:
for %%A in ("dist\miniZ_MCP_Professional.exe") do (
    set size=%%~zA
    set /a sizeMB=%%~zA/1024/1024
)
echo %sizeMB% MB
echo.

echo ============================================================
echo 📋 CÁC LICENSE KEY TEST
echo ============================================================
echo.
echo 📦 STANDARD Keys (Test):
echo    MINIZ-STD5-G3YE-7L5J-57ND
echo    MINIZ-STDD-NF2L-4Z3N-PXCV
echo    MINIZ-STD4-QKJT-8JF5-HVVJ
echo.
echo 💎 PRO Keys (Test):
echo    MINIZ-PRO6-D8SM-J3NK-G7R4
echo    MINIZ-PROB-ZDFC-LDS7-UB32
echo.
echo 🏆 ENTERPRISE Keys (Test):
echo    MINIZ-ENTJ-VFTV-K6VQ-8UZD
echo    MINIZ-ENTU-6KYR-UYX8-CN99
echo.

echo ============================================================
echo 🔧 HƯỚNG DẪN TEST
echo ============================================================
echo.
echo 1. Chạy file EXE: dist\miniZ_MCP_Professional.exe
echo 2. Khi được yêu cầu, nhập MỘT key test từ danh sách trên
echo 3. Kiểm tra activation thành công
echo 4. Kiểm tra file license được tạo tại:
echo    %%LOCALAPPDATA%%\miniZ_MCP\.license\license.enc
echo 5. Restart app và verify license tự động validate
echo.

echo ============================================================
echo 📂 EMBEDDED FILES IN EXE
echo ============================================================
echo.
echo ✅ LICENSE_KEYS.json (150 keys)
echo    - 100 STANDARD keys (1 device)
echo    - 40 PRO keys (2 devices)
echo    - 10 ENTERPRISE keys (5 devices)
echo.
echo ✅ license_system.py (Hardware-locked system)
echo    - CPU ID + Motherboard Serial binding
echo    - PBKDF2HMAC encryption (100,000 iterations)
echo    - AES-256 Fernet encryption
echo.
echo ✅ xiaozhi_endpoints.json (API configuration)
echo.

echo ============================================================
echo 🔐 SECURITY FEATURES
echo ============================================================
echo.
echo ✅ Hardware ID Binding
echo    - Unique per machine (CPU + Motherboard)
echo    - Cannot copy license.enc to another PC
echo.
echo ✅ License Encryption
echo    - PBKDF2HMAC-SHA256 key derivation
echo    - 100,000 iterations for brute-force resistance
echo    - Fernet symmetric encryption
echo.
echo ✅ Checksum Validation
echo    - MD5-based with alphanumeric mapping
echo    - Format: MINIZ-XXXX-XXXX-XXXX-XXXX
echo    - Invalid keys rejected before activation
echo.

echo ============================================================
echo 📊 BUILD INFORMATION
echo ============================================================
echo.
echo Version: 4.3.0
echo Build Date: 2025-01-08
echo Build Tool: PyInstaller 6.17.0
echo Python: 3.13.9
echo Architecture: x64
echo Type: Single-file EXE
echo.

echo ============================================================
echo 💡 NEXT STEPS
echo ============================================================
echo.
echo 1. TEST: Run .\dist\miniZ_MCP_Professional.exe
echo 2. VERIFY: Check license activation with test key
echo 3. VALIDATE: Confirm hardware binding works
echo 4. DISTRIBUTE: Copy EXE + LICENSE_ACTIVATION_GUIDE.md
echo.

pause
