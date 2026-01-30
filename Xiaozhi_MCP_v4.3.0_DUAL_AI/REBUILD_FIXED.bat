@echo off
chcp 65001 > nul
title Build miniZ MCP - Fixed Version

echo.
echo ════════════════════════════════════════════════════════
echo 🔨 BUILD LẠI FILE EXE - ĐÃ SỬA LỖI PERMISSION
echo ════════════════════════════════════════════════════════
echo.
echo ✅ Đã sửa 3 lỗi permission denied:
echo    1. miniz_license.json
echo    2. music_folder_config.json
echo    3. conversation_history.json
echo.
echo ⏳ Thời gian build: 2-3 phút
echo 🚫 ĐỪNG ĐÓNG CỬA SỔ NÀY!
echo.
echo ════════════════════════════════════════════════════════
echo.

echo [1/5] Xóa build cũ...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
echo       ✅ Đã xóa

echo.
echo [2/5] Build executable với PyInstaller...
python -m PyInstaller xiaozhi_installer.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo ❌ BUILD THẤT BẠI!
    pause
    exit /b 1
)

echo.
echo [3/5] Kiểm tra file exe...
if exist "dist\miniZ_MCP_v4.3.0_Professional.exe" (
    for %%F in ("dist\miniZ_MCP_v4.3.0_Professional.exe") do (
        set size=%%~zF
        set /a sizeMB=%%~zF/1024/1024
    )
    echo       ✅ File exe: !sizeMB! MB
) else (
    echo       ❌ Không tìm thấy file exe!
    pause
    exit /b 1
)

echo.
echo [4/5] Xóa installer cũ...
if exist "installer_output\*.exe" (
    del /f /q "installer_output\*.exe" 2>nul
    echo       ✅ Đã xóa installer cũ
)

echo.
echo [5/5] Build installer với Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
if errorlevel 1 (
    echo.
    echo ❌ BUILD INSTALLER THẤT BẠI!
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════
echo.
echo ✅ BUILD HOÀN TẤT!
echo.
echo 📦 Kết quả:
dir /b "installer_output\*.exe" 2>nul
for %%F in ("installer_output\*.exe") do (
    set /a installerMB=%%~zF/1024/1024
    echo    └─ %%~nxF (!installerMB! MB)
)
echo.
echo 🎉 Sẵn sàng phân phối cho khách hàng!
echo.
echo ════════════════════════════════════════════════════════
echo.
pause
