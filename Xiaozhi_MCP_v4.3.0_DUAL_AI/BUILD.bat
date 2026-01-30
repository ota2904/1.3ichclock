@echo off
REM ============================================
REM miniZ MCP v4.3.0 Professional - Build Script
REM ============================================

echo.
echo ============================================
echo   miniZ MCP v4.3.0 - Professional Edition
echo   BUILD AUTOMATION SCRIPT
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python khong duoc cai dat!
    echo Vui long cai dat Python 3.8+ tu https://python.org
    pause
    exit /b 1
)

echo [1/5] Kiem tra PyInstaller...
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Cai dat PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Khong the cai dat PyInstaller!
        pause
        exit /b 1
    )
)
echo [OK] PyInstaller da san sang.

echo.
echo [2/5] Kiem tra dependencies...
pip install -r requirements.txt --quiet
echo [OK] Tat ca dependencies da duoc cai dat.

echo.
echo [3/5] Xoa build/dist cu (neu co)...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
echo [OK] Da xoa build/dist cu.

echo.
echo [4/5] Build executable voi PyInstaller...
echo.
echo ----------------------------------------
echo BẮT ĐẦU BUILD...
echo ----------------------------------------
echo.

pyinstaller xiaozhi_installer.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [ERROR] Build that bai!
    echo Vui long kiem tra log ben tren.
    pause
    exit /b 1
)

echo.
echo [5/5] Kiem tra file exe...
if exist "dist\miniZ_MCP_v4.3.0_Professional.exe" (
    echo.
    echo ============================================
    echo   ✅ BUILD THANH CONG!
    echo ============================================
    echo.
    echo File executable:
    echo   dist\miniZ_MCP_v4.3.0_Professional.exe
    echo.
    dir "dist\miniZ_MCP_v4.3.0_Professional.exe" | findstr "miniZ"
    echo.
    echo ----------------------------------------
    echo BUOC TIEP THEO:
    echo ----------------------------------------
    echo 1. Test executable: cd dist ^&^& miniZ_MCP_v4.3.0_Professional.exe
    echo 2. Neu muon tao installer: Build voi Inno Setup (installer.iss)
    echo 3. Xem huong dan: BUILD_GUIDE.md
    echo.
) else (
    echo.
    echo [ERROR] Khong tim thay file exe trong dist/
    echo Vui long kiem tra log loi ben tren.
    pause
    exit /b 1
)

echo.
pause
