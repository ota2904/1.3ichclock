@echo off
chcp 65001 > nul
echo.
echo ================================================================
echo 🧪 TEST GEMINI AI + KNOWLEDGE BASE INTEGRATION
echo ================================================================
echo.
echo This test will:
echo   1. Create mock documents
echo   2. Index them into Knowledge Base
echo   3. Ask Gemini questions
echo   4. Verify Gemini uses KB data automatically
echo.
echo ⚠️  Make sure server is running: python xiaozhi_final.py
echo.
pause
echo.

python test_gemini_kb_integration.py

echo.
pause
