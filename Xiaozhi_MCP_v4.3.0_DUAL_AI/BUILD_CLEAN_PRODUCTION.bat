@echo off
chcp 65001 > nul
echo.
echo ================================================================
echo 🔒 BUILD CLEAN PRODUCTION EXE
echo ================================================================
echo.
echo Removing old builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo.
echo Building miniZ_MCP_Clean.exe...
echo This will take 5-10 minutes, please wait...
echo.

python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name miniZ_MCP_Clean ^
    --icon logo.ico ^
    --add-data "knowledge_index.json;." ^
    --hidden-import google.generativeai ^
    --hidden-import openai ^
    --hidden-import fastapi ^
    --hidden-import uvicorn ^
    --collect-all google.generativeai ^
    xiaozhi_final.py

echo.
if exist "dist\miniZ_MCP_Clean.exe" (
    echo ================================================================
    echo ✅ BUILD SUCCESSFUL!
    echo ================================================================
    echo.
    for %%F in ("dist\miniZ_MCP_Clean.exe") do (
        set /a "size_mb=%%~zF / 1048576"
        echo 📁 Output: dist\miniZ_MCP_Clean.exe
        echo 📊 Size: !size_mb! MB
    )
    echo.
    echo 🔒 SECURITY: No API keys included in this build
    echo 📝 Users must provide their own API keys in settings
    echo.
) else (
    echo ❌ BUILD FAILED - EXE not found
)

pause
