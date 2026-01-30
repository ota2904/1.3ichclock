@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
color 0A
title miniZ MCP v4.3.0 - Build FREE Edition (32-bit + 64-bit Compatible)

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║       miniZ MCP v4.3.0 - BUILD FREE EDITION                    ║
echo ║                                                                 ║
echo ║  ✓ Không cần License Key                                       ║
echo ║  ✓ Khởi động cùng Windows                                      ║
echo ║  ✓ Đầy đủ thư viện                                             ║
echo ║  ✓ Bấm là chạy                                                 ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Get Python path
set "PYTHON_PATH=C:\Users\congh\AppData\Local\Python\pythoncore-3.14-64\python.exe"

REM Check if Python exists
if not exist "%PYTHON_PATH%" (
    echo ❌ Python không tìm thấy tại: %PYTHON_PATH%
    echo    Đang tìm Python khác...
    where python >nul 2>&1
    if %errorlevel% == 0 (
        set "PYTHON_PATH=python"
        echo ✅ Sử dụng Python từ PATH
    ) else (
        echo ❌ Không tìm thấy Python!
        pause
        exit /b 1
    )
)

echo [1/5] Kiểm tra Python...
"%PYTHON_PATH%" --version
echo.

echo [2/5] Xóa build cũ...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q *.spec 2>nul
del /q output\miniZ_MCP_FREE*.exe 2>nul
echo ✅ Đã xóa build cũ
echo.

echo [3/5] Cài đặt thư viện...
"%PYTHON_PATH%" -m pip install pyinstaller --quiet
echo ✅ PyInstaller ready
echo.

echo [4/5] Đang build EXE (Vui lòng chờ 2-3 phút)...
echo.

REM Create output directory
if not exist output mkdir output

REM Build với PyInstaller - bao gồm tất cả thư viện
"%PYTHON_PATH%" -m PyInstaller ^
    --onefile ^
    --console ^
    --name "miniZ_MCP_v4.3.0_FREE" ^
    --distpath "output" ^
    --icon "icons/app_icon.ico" ^
    --add-data "static;static" ^
    --add-data "templates;templates" ^
    --add-data "logo.png;." ^
    --add-data "icon.ico;." ^
    --add-data "xiaozhi_final.py;." ^
    --hidden-import=pynput ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pynput.keyboard._win32 ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pynput.mouse._win32 ^
    --hidden-import=keyboard ^
    --hidden-import=undetected_chromedriver ^
    --hidden-import=yt_dlp ^
    --hidden-import=pytube ^
    --hidden-import=mutagen ^
    --hidden-import=eyed3 ^
    --hidden-import=filetype ^
    --hidden-import=deprecation ^
    --hidden-import=anthropic ^
    --hidden-import=google.generativeai ^
    --hidden-import=uvicorn ^
    --hidden-import=fastapi ^
    --hidden-import=starlette ^
    --hidden-import=websockets ^
    --hidden-import=aiohttp ^
    --hidden-import=httpx ^
    --hidden-import=PIL ^
    --hidden-import=cv2 ^
    --hidden-import=numpy ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=selenium ^
    --hidden-import=pyautogui ^
    --hidden-import=speech_recognition ^
    --hidden-import=gtts ^
    --hidden-import=pygame ^
    --hidden-import=pyaudio ^
    --hidden-import=sounddevice ^
    --hidden-import=soundfile ^
    --hidden-import=openai ^
    --hidden-import=tiktoken ^
    --hidden-import=chromadb ^
    --hidden-import=sentence_transformers ^
    --hidden-import=lxml ^
    --hidden-import=bs4 ^
    --hidden-import=docx ^
    --hidden-import=openpyxl ^
    --hidden-import=comtypes ^
    --hidden-import=win32com ^
    --hidden-import=win32gui ^
    --hidden-import=win32api ^
    --hidden-import=win32con ^
    --hidden-import=wmi ^
    --hidden-import=psutil ^
    --hidden-import=tzdata ^
    --hidden-import=jinja2 ^
    --hidden-import=multipart ^
    --hidden-import=python-multipart ^
    --hidden-import=uvloop ^
    --hidden-import=cryptography ^
    --hidden-import=winreg ^
    --collect-all pynput ^
    --collect-all google.generativeai ^
    --collect-all anthropic ^
    --collect-all keyboard ^
    --collect-all yt_dlp ^
    --collect-all pytube ^
    --collect-all mutagen ^
    --collect-all eyed3 ^
    --collect-all undetected_chromedriver ^
    --collect-all chromadb ^
    --collect-all sentence_transformers ^
    --collect-all tiktoken ^
    --collect-submodules uvicorn ^
    --collect-submodules starlette ^
    --collect-submodules fastapi ^
    --noconfirm ^
    --clean ^
    xiaozhi_final.py

echo.

if exist "output\miniZ_MCP_v4.3.0_FREE.exe" (
    echo [5/5] Kiểm tra kết quả...
    echo.
    for %%F in ("output\miniZ_MCP_v4.3.0_FREE.exe") do (
        set "SIZE=%%~zF"
        set /a "SIZE_MB=!SIZE!/1048576"
        echo ╔════════════════════════════════════════════════════════════════╗
        echo ║                    ✅ BUILD THÀNH CÔNG!                        ║
        echo ╠════════════════════════════════════════════════════════════════╣
        echo ║  📁 File: output\miniZ_MCP_v4.3.0_FREE.exe                     ║
        echo ║  📦 Size: ~!SIZE_MB! MB                                        ║
        echo ║                                                                 ║
        echo ║  ĐẶC ĐIỂM:                                                     ║
        echo ║  ✓ Không cần License Key                                       ║
        echo ║  ✓ Tự động khởi động cùng Windows                              ║
        echo ║  ✓ Đầy đủ thư viện AI + Media + Automation                    ║
        echo ║  ✓ Chạy được trên mọi máy Windows 10/11                        ║
        echo ╚════════════════════════════════════════════════════════════════╝
    )
) else (
    echo ❌ BUILD THẤT BẠI!
    echo    Kiểm tra log để biết chi tiết lỗi
)

echo.
echo Nhấn phím bất kỳ để thoát...
pause >nul
