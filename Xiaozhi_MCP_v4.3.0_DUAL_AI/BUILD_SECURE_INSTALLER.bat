@echo off
chcp 65001 >nul
echo.
echo ════════════════════════════════════════════════════════════════════════
echo     BUILD MINIZ MCP v4.3.3 SECURE INSTALLER WITH INNO SETUP
echo ════════════════════════════════════════════════════════════════════════
echo.
echo 📦 FEATURES:
echo    ✅ Full license agreement
echo    ✅ No API tokens included (secure)
echo    ✅ Auto-startup option
echo    ✅ Complete terms and conditions
echo    ✅ User must accept all terms
echo.

REM Check if EXE exists
if not exist "dist\miniZ_MCP_v4.3.3_Full.exe" (
    echo ❌ ERROR: miniZ_MCP_v4.3.3_Full.exe not found in dist folder
    echo Please build the EXE first with: python build_exe.py
    echo.
    pause
    exit /b 1
)

REM Check Inno Setup installation
set "InnoSetup=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%InnoSetup%" (
    echo ❌ ERROR: Inno Setup 6 not found
    echo Please install from: https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo ✅ Found EXE: dist\miniZ_MCP_v4.3.3_Full.exe
echo ✅ Found Inno Setup: %InnoSetup%
echo.
echo 🔨 Building installer...
echo.

REM Build installer
"%InnoSetup%" "installer_v4.3.3_secure.iss"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ════════════════════════════════════════════════════════════════════════
    echo       ✅ INSTALLER BUILD SUCCESSFUL!
    echo ════════════════════════════════════════════════════════════════════════
    echo.
    
    if exist "installer_output\miniZ_MCP_v4.3.3_Secure_Setup.exe" (
        for %%F in ("installer_output\miniZ_MCP_v4.3.3_Secure_Setup.exe") do (
            echo 📦 INSTALLER FILE:
            echo    Name: %%~nxF
            echo    Size: %%~zF bytes
            echo    Path: %%~dpF
            echo.
        )
        
        echo ✨ SECURITY FEATURES:
        echo    ✅ NO API keys/tokens included
        echo    ✅ User must configure own keys
        echo    ✅ Full license agreement required
        echo    ✅ Auto-startup option available
        echo    ✅ Complete terms and conditions
        echo.
        echo 🚀 READY TO DISTRIBUTE!
        echo.
        
        REM Open output folder
        explorer "installer_output"
    )
) else (
    echo.
    echo ❌ BUILD FAILED! Check errors above.
    echo.
)

pause
