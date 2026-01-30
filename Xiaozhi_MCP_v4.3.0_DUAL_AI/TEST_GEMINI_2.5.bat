@echo off
chcp 65001 >nul
echo.
echo ══════════════════════════════════════════════════════════
echo          🧪 TEST GEMINI 2.5 FLASH - miniZ MCP
echo ══════════════════════════════════════════════════════════
echo.

REM Check if GEMINI_API_KEY is set
if "%GEMINI_API_KEY%"=="" (
    echo ❌ GEMINI_API_KEY chưa được set!
    echo.
    echo 💡 Hãy set API key trước:
    echo    set GEMINI_API_KEY=your_api_key_here
    echo.
    echo 🔑 Lấy API key tại: https://aistudio.google.com/apikey
    echo.
    pause
    exit /b 1
)

echo ✅ API Key đã được set
echo.

echo 🔍 Đang test Gemini 2.5 Flash...
echo.

python quick_test_gemini.py

echo.
echo ══════════════════════════════════════════════════════════
echo.
pause
