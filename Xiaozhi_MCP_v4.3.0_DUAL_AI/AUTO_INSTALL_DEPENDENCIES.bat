@echo off
REM ============================================================
REM miniZ MCP v4.3.2 - Auto Install Dependencies
REM Cài đặt tự động tất cả thư viện cần thiết
REM ============================================================

color 0A
title miniZ MCP - Auto Installation

echo.
echo ============================================================
echo    miniZ MCP v4.3.2 - AUTOMATIC INSTALLATION
echo ============================================================
echo.
echo [1/5] Kiem tra Python...

REM Kiểm tra Python đã cài chưa
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python chua duoc cai dat!
    echo.
    echo Vui long cai dat Python 3.11+ tu:
    echo https://www.python.org/downloads/
    echo.
    echo Trong qua trinh cai dat, HAY CHON:
    echo  [x] Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo [OK] Python da duoc cai dat
python --version

echo.
echo [2/5] Nang cap pip...
python -m pip install --upgrade pip --quiet

echo.
echo [3/5] Cai dat thu vien co ban...
python -m pip install fastapi==0.104.1 uvicorn[standard]==0.38.0 pydantic==2.5.0 --quiet

echo.
echo [4/5] Cai dat thu vien AI (Gemini, OpenAI)...
python -m pip install google-generativeai==0.8.3 openai==1.54.0 --quiet

echo.
echo [5/5] Cai dat cac thu vien con lai...
python -m pip install psutil requests websockets pyautogui pyperclip python-multipart httpx beautifulsoup4 ddgs --quiet
python -m pip install python-vlc youtube-search-python selenium webdriver-manager --quiet
python -m pip install pywin32 comtypes SpeechRecognition PyAudio pycaw screen-brightness-control --quiet
python -m pip install pystray Pillow --quiet

echo.
echo ============================================================
echo    CAI DAT HOAN TAT!
echo ============================================================
echo.
echo Tat ca cac thu vien da duoc cai dat thanh cong.
echo Ban co the khoi dong miniZ MCP bang cach chay START.bat
echo.

REM Tạo file đánh dấu cài đặt thành công
echo installed > "%~dp0.dependencies_installed"
echo %date% %time% >> "%~dp0.dependencies_installed"

echo Nhan phim bat ky de dong cua so...
pause >nul
