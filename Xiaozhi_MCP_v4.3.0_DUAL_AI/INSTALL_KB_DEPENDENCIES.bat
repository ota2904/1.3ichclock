@echo off
echo ============================================
echo  INSTALLING KNOWLEDGE BASE DEPENDENCIES
echo ============================================
echo.

cd /d "%~dp0"

echo Installing PDF extraction library...
call .venv\Scripts\pip install PyPDF2

echo.
echo Installing Word document library...
call .venv\Scripts\pip install python-docx

echo.
echo Installing RTF library...
call .venv\Scripts\pip install striprtf

echo.
echo Installing Excel library...
call .venv\Scripts\pip install openpyxl

echo.
echo ============================================
echo  INSTALLATION COMPLETE!
echo ============================================
echo.
echo Next steps:
echo 1. Restart the server
echo 2. Go to Knowledge Base in Web UI
echo 3. Click "Clear Index" to delete old index
echo 4. Click "Index All" to re-index with proper extraction
echo.
pause
