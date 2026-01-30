@echo off
chcp 65001 > nul
echo.
echo ================================================================
echo 🔒 BUILD CLEAN PRODUCTION EXE - NO SENSITIVE INFORMATION
echo ================================================================
echo.
echo This will create a clean production build WITHOUT:
echo   ❌ Hardcoded API keys
echo   ❌ Test files
echo   ❌ License databases
echo   ❌ Conversation history
echo.
echo Users will need to provide their own API keys in settings.
echo.
pause
echo.

python build_clean_exe.py

echo.
pause
