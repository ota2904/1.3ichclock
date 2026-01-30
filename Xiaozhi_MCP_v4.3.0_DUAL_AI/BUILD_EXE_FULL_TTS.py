#!/usr/bin/env python3
"""
🚀 miniZ MCP - Full Features EXE Builder v4.3.5
Build file EXE đầy đủ tính năng mới + TTS tiếng Việt:
- ✅ Tất cả 144+ tools mới
- ✅ Hardware detection (CPU/GPU generation)
- ✅ Password-style API input với eye icon
- ✅ TTS tiếng Việt (pyttsx3 + gTTS + edge-tts)
- ✅ Lưu và giữ thông tin API khi khởi động lại
- ✅ Mã hóa API keys an toàn
- ✅ VLC Music Player tích hợp
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "miniZ_MCP_v4.3.5_TTS"
APP_VERSION = "4.3.5"
MAIN_SCRIPT = "xiaozhi_final.py"

BASE_DIR = Path(__file__).parent.resolve()
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"

# ============================================================
# PYINSTALLER COMMAND
# ============================================================

def build_exe():
    """Build EXE với PyInstaller"""
    
    print("=" * 60)
    print(f"🚀 miniZ MCP Full Features + TTS Builder v{APP_VERSION}")
    print("=" * 60)
    
    # Step 1: Clean old build
    print("\n[1/4] Dọn dẹp build cũ...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    DIST_DIR.mkdir(exist_ok=True)
    print("  ✅ Đã dọn dẹp")
    
    # Step 2: Check dependencies
    print("\n[2/4] Kiểm tra dependencies...")
    required_packages = [
        'pyinstaller', 'fastapi', 'uvicorn', 'websockets', 'psutil',
        'pyautogui', 'pystray', 'pillow', 'pyttsx3', 'gtts', 'vlc'
    ]
    for pkg in required_packages:
        try:
            if pkg == 'pillow':
                __import__('PIL')
            elif pkg == 'pyinstaller':
                __import__('PyInstaller')
            else:
                __import__(pkg.replace('-', '_'))
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ⚠️ {pkg} - sẽ cố gắng build anyway")
    
    # Step 3: Prepare data files
    print("\n[3/4] Chuẩn bị files...")
    data_files = []
    
    # Add data files nếu tồn tại
    files_to_add = [
        ("xiaozhi_endpoints.json", "."),
        ("xiaozhi_endpoints_template.json", "."),
        ("rag_config.json", "."),
        ("custom_music_folder.txt", "."),
    ]
    
    for src, dest in files_to_add:
        src_path = BASE_DIR / src
        if src_path.exists():
            data_files.append(f'--add-data={src};{dest}')
            print(f"  ✅ {src}")
    
    # Add folders nếu tồn tại
    folders_to_add = [
        ("music_library", "music_library"),
        ("knowledge_base", "knowledge_base"),
    ]
    
    for src, dest in folders_to_add:
        src_path = BASE_DIR / src
        if src_path.exists():
            data_files.append(f'--add-data={src};{dest}')
            print(f"  ✅ {src}/")
    
    # Step 4: Build with PyInstaller
    print("\n[4/4] Building EXE với PyInstaller...")
    print("  ⏳ Quá trình này có thể mất 3-5 phút...")
    
    # Hidden imports cho đầy đủ tính năng
    hidden_imports = [
        # FastAPI & Web
        'uvicorn', 'uvicorn.logging', 'uvicorn.protocols',
        'uvicorn.protocols.http', 'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan', 'uvicorn.lifespan.on',
        'fastapi', 'fastapi.responses', 'fastapi.staticfiles',
        'starlette', 'starlette.responses', 'starlette.routing',
        'pydantic', 'pydantic_core',
        'websockets', 'websockets.client', 'websockets.legacy.client',
        'aiohttp', 'httpx',
        
        # System control
        'psutil', 'pyautogui', 'pynput', 'pynput.keyboard', 'pynput.mouse',
        'screen_brightness_control', 'pycaw', 'pycaw.pycaw',
        'comtypes', 'comtypes.client',
        
        # Windows
        'wmi', 'pythoncom', 'win32com', 'win32com.client',
        'win32api', 'win32gui', 'win32con', 'winreg',
        'ctypes', 'ctypes.wintypes',
        
        # AI APIs
        'google.generativeai', 'google.ai', 'openai',
        
        # Search & RAG
        'duckduckgo_search', 'duckduckgo_search.duckduckgo_search',
        'bs4', 'requests',
        
        # TTS - Tiếng Việt
        'pyttsx3', 'pyttsx3.drivers', 'pyttsx3.drivers.sapi5',
        'gtts', 'gtts.tts',
        'edge_tts',
        
        # VLC
        'vlc',
        
        # Tray
        'pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw',
        
        # Crypto
        'cryptography', 'cryptography.fernet',
        
        # GPU detection
        'GPUtil',
        
        # Encoding
        'encodings', 'encodings.utf_8', 'encodings.ascii',
        'encodings.cp1252', 'encodings.latin_1',
        
        # importlib for modern package detection
        'importlib', 'importlib.metadata',
    ]
    
    # Build command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=' + APP_NAME,
        '--onefile',
        '--windowed',  # No console
        '--clean',
        '--noconfirm',
        f'--distpath={DIST_DIR}',
        f'--workpath={BUILD_DIR}',
    ]
    
    # Add hidden imports
    for imp in hidden_imports:
        cmd.append(f'--hidden-import={imp}')
    
    # Add data files
    cmd.extend(data_files)
    
    # Add icon nếu có
    icon_path = BASE_DIR / "icon.ico"
    if icon_path.exists():
        cmd.append(f'--icon={icon_path}')
    
    # Add main script
    cmd.append(str(BASE_DIR / MAIN_SCRIPT))
    
    # Run PyInstaller
    print(f"\n  🔧 Running: pyinstaller {APP_NAME}...")
    result = subprocess.run(cmd, cwd=BASE_DIR)
    
    if result.returncode == 0:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print("\n" + "=" * 60)
            print("✅ BUILD THÀNH CÔNG!")
            print("=" * 60)
            print(f"\n📦 File EXE: {exe_path}")
            print(f"📊 Kích thước: {size_mb:.1f} MB")
            print(f"📅 Build time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n🎯 Tính năng:")
            print("  - 144+ tools AI")
            print("  - Hardware detection (CPU/GPU generation)")
            print("  - TTS tiếng Việt (pyttsx3 + gTTS)")
            print("  - Password-style API input")
            print("  - VLC Music Player")
            print("  - Auto-save config")
            
            # Copy additional files to dist
            print("\n📁 Copy files bổ sung...")
            for f in ["xiaozhi_endpoints_template.json", "CUSTOMER_README.md", "HUONG_DAN_NHANH_v4.3.0.md"]:
                src = BASE_DIR / f
                if src.exists():
                    shutil.copy(src, DIST_DIR / f)
                    print(f"  ✅ {f}")
            
            return True
    
    print("\n❌ BUILD THẤT BẠI!")
    return False


if __name__ == "__main__":
    success = build_exe()
    if success:
        print("\n🎉 Hoàn thành! File EXE trong thư mục: dist/")
    else:
        print("\n⚠️ Có lỗi xảy ra. Kiểm tra log ở trên.")
    
    input("\nNhấn Enter để đóng...")
