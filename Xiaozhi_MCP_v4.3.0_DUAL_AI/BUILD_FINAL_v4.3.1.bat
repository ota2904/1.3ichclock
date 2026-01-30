@echo off
chcp 65001 > nul
cls
echo.
echo ================================================================
echo 🔨 BUILD miniZ MCP v4.3.1 FINAL - WITH ALL FIXES
echo ================================================================
echo.
echo Fixes included:
echo   ✅ Gemini 2.5 Flash upgrade
echo   ✅ Gemini AI + Knowledge Base integration
echo   ✅ YouTube direct video (auto-detect)
echo   ✅ No hardcoded API keys
echo   ✅ Clean production build
echo.
echo ⏱️  This will take 5-10 minutes. Please wait...
echo.
pause
echo.

echo 🧹 Cleaning old builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo ✅ Cleaned
echo.

echo 🔨 Starting PyInstaller build...
echo.
python -m PyInstaller ^
    --clean ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name "miniZ_MCP_v4.3.1_FINAL_FIXED" ^
    --icon logo.ico ^
    --add-data "knowledge_index.json;." ^
    --hidden-import google.generativeai ^
    --hidden-import openai ^
    --hidden-import anthropic ^
    --hidden-import fastapi ^
    --hidden-import uvicorn ^
    --hidden-import pydantic ^
    --hidden-import tiktoken ^
    --hidden-import numpy ^
    --hidden-import sklearn ^
    --collect-all google.generativeai ^
    xiaozhi_final.py

echo.
if exist "dist\miniZ_MCP_v4.3.1_FINAL_FIXED.exe" (
    echo ================================================================
    echo ✅ BUILD SUCCESSFUL!
    echo ================================================================
    echo.
    for %%F in ("dist\miniZ_MCP_v4.3.1_FINAL_FIXED.exe") do (
        set size=%%~zF
        set /a size_mb=%%~zF / 1048576
        echo 📁 Output: dist\miniZ_MCP_v4.3.1_FINAL_FIXED.exe
        echo 📊 Size: !size_mb! MB
        echo 📅 Built: %%~tF
    )
    echo.
    echo ✨ FEATURES IN THIS BUILD:
    echo    🤖 Gemini 2.5 Flash (latest model)
    echo    📚 Auto Knowledge Base integration
    echo    📺 YouTube direct video (smart detect)
    echo    🔒 No API keys (user provides own)
    echo    💾 Save/load config working
    echo    🎵 Custom music folder support
    echo.
    echo 🎉 READY TO USE!
    echo.
    explorer dist
) else (
    echo ================================================================
    echo ❌ BUILD FAILED
    echo ================================================================
    echo.
    echo Check errors above for details.
    echo.
)

pause
