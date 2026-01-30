@echo off
chcp 65001 >nul
title 🏗️ Build miniZ MCP Professional EXE with License System
color 0B

echo.
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║                                                               ║
echo ║     🏗️  BUILD miniZ MCP PROFESSIONAL EXE                      ║
echo ║              With 150 License Keys Embedded                   ║
echo ║                                                               ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Check Python
echo [1/6] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found!
    pause
    exit /b 1
)
python --version
echo ✅ Python OK

REM Step 2: Check PyInstaller
echo.
echo [2/6] Checking PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ⚠️  PyInstaller not installed. Installing...
    pip install pyinstaller
) else (
    echo ✅ PyInstaller installed
)

REM Step 3: Check required files
echo.
echo [3/6] Checking required files...
set MISSING=0

if not exist "xiaozhi_final.py" (
    echo ❌ Missing: xiaozhi_final.py
    set MISSING=1
) else (
    echo ✅ xiaozhi_final.py
)

if not exist "license_system.py" (
    echo ❌ Missing: license_system.py
    set MISSING=1
) else (
    echo ✅ license_system.py
)

if not exist "LICENSE_KEYS.json" (
    echo ❌ Missing: LICENSE_KEYS.json
    set MISSING=1
) else (
    echo ✅ LICENSE_KEYS.json
)

if %MISSING%==1 (
    echo.
    echo ❌ Missing required files!
    pause
    exit /b 1
)

REM Step 4: Install dependencies
echo.
echo [4/6] Installing dependencies...
pip install -r requirements.txt --quiet
echo ✅ Dependencies installed

REM Step 5: Build EXE
echo.
echo [5/6] Building EXE with PyInstaller...
echo ⏳ This may take 2-5 minutes...
echo.

python -m PyInstaller --clean ^
    --onefile ^
    --name "miniZ_MCP_Professional" ^
    --add-data "LICENSE_KEYS.json;." ^
    --add-data "LICENSE_ACTIVATION_GUIDE.md;." ^
    --add-data "xiaozhi_endpoints.json;." ^
    --add-data "requirements.txt;." ^
    --add-data "README.md;." ^
    --add-data "LICENSE;." ^
    --add-data "music_library;music_library" ^
    --hidden-import license_system ^
    --hidden-import license_manager ^
    --hidden-import google.generativeai ^
    --hidden-import cryptography ^
    --hidden-import cryptography.fernet ^
    --hidden-import cryptography.hazmat.primitives.kdf.pbkdf2 ^
    --console ^
    xiaozhi_final.py

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

REM Step 6: Verify output
echo.
echo [6/6] Verifying build...

if exist "dist\miniZ_MCP_Professional.exe" (
    echo.
    echo ╔═══════════════════════════════════════════════════════════════╗
    echo ║                                                               ║
    echo ║              ✅ BUILD SUCCESSFUL!                             ║
    echo ║                                                               ║
    echo ╚═══════════════════════════════════════════════════════════════╝
    echo.
    
    REM Get file size
    for %%F in ("dist\miniZ_MCP_Professional.exe") do (
        set size=%%~zF
        set /a size_mb=!size! / 1048576
    )
    
    echo 📦 Output: dist\miniZ_MCP_Professional.exe
    echo 💾 Size: %size_mb% MB
    echo.
    echo ✨ FEATURES INCLUDED:
    echo    • 150 License Keys Embedded (100 STD + 40 PRO + 10 ENT)
    echo    • Hardware-Locked License System
    echo    • 141 AI Tools
    echo    • Smart Conversation Analyzer
    echo    • Multi-Device WebSocket MCP
    echo    • VLC Music Player Integration
    echo    • Web Dashboard UI
    echo.
    echo 🔑 LICENSE KEYS:
    echo    • File: LICENSE_KEYS.json (embedded in EXE)
    echo    • Standard: 100 keys (1 device each)
    echo    • Pro: 40 keys (2 devices each)
    echo    • Enterprise: 10 keys (5 devices each)
    echo.
    echo 📋 DISTRIBUTION:
    echo    1. Give customer: miniZ_MCP_Professional.exe
    echo    2. Provide 1 license key from LICENSE_KEYS.json
    echo    3. Customer runs EXE → enters license key
    echo    4. License binds to their hardware
    echo.
    echo 📁 Opening output folder...
    explorer dist
    
) else (
    echo ❌ EXE file not found!
    echo Check build errors above.
)

echo.
pause
