#!/usr/bin/env python3
"""
🚀 miniZ MCP - Build for Python 3.14 with ALL dependencies
Build file EXE với đầy đủ thư viện cho Python 3.14
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║          🚀 miniZ MCP - Build for Python 3.14              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

BASE_DIR = Path(__file__).parent.resolve()
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Full hidden imports for Python 3.14
HIDDEN_IMPORTS = [
    # FastAPI & Web
    'uvicorn', 'uvicorn.logging', 'uvicorn.protocols', 'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 
    'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on',
    'fastapi', 'fastapi.responses', 'fastapi.staticfiles', 'fastapi.middleware',
    'starlette', 'starlette.responses', 'starlette.middleware',
    'pydantic', 'pydantic_core', 'pydantic.v1',
    'websockets', 'websockets.client', 'websockets.server',
    'aiohttp', 'httpx', 'httpcore',
    
    # System control
    'psutil', 'pyautogui', 'pynput', 'pynput.keyboard', 'pynput.mouse',
    'screen_brightness_control', 'pycaw', 'pycaw.pycaw',
    'comtypes', 'comtypes.client',
    
    # Windows
    'wmi', 'pythoncom', 'win32com', 'win32com.client',
    'win32api', 'win32gui', 'win32con', 'winreg',
    'ctypes', 'ctypes.wintypes',
    
    # AI APIs  
    'google.generativeai', 'google.ai', 'google.ai.generativelanguage',
    'google.genai', 'google.genai.types',
    'openai',
    
    # Search & RAG
    'duckduckgo_search', 'duckduckgo_search.duckduckgo_search',
    'bs4', 'beautifulsoup4', 'lxml',
    
    # VLC
    'vlc',
    
    # Tray & GUI
    'pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
    
    # PDF & Documents (for Knowledge Base)
    'PyPDF2', 'PyPDF2.pdf',
    'openpyxl', 'openpyxl.workbook', 'openpyxl.worksheet',
    'docx', 'docx.document',
    'striprtf', 'striprtf.striprtf',
    
    # Audio
    'winsound', 'struct',
    
    # Async
    'asyncio', 'concurrent', 'concurrent.futures',
    
    # Encoding
    'encodings', 'encodings.utf_8', 'encodings.ascii', 'encodings.latin_1',
    'encodings.cp1252', 'encodings.cp437',
    
    # Standard libs
    'json', 'pathlib', 'datetime', 'threading', 'queue', 'hashlib',
    'base64', 'urllib', 'urllib.parse', 'urllib.request',
    're', 'math', 'random', 'time', 'os', 'sys', 'io', 'tempfile',
    'zipfile', 'xml', 'xml.etree', 'xml.etree.ElementTree',
    
    # Fuzzy matching
    'difflib', 'unicodedata',
    
    # Browser
    'webbrowser',
]

# Data files to include
DATA_FILES = [
    ('rag_system.py', '.'),
    ('rag_config.json', '.'),
    ('security_module.py', '.'),
    ('startup_manager.py', '.'),
    ('activation_window.py', '.'),
    ('config_manager.py', '.'),
]

# Check if music_library exists
if (BASE_DIR / 'music_library').exists():
    DATA_FILES.append(('music_library', 'music_library'))

print(f"📁 Base directory: {BASE_DIR}")
print(f"📁 Output directory: {OUTPUT_DIR}")
print(f"🐍 Python version: {sys.version}")
print(f"📦 Hidden imports: {len(HIDDEN_IMPORTS)}")

# Build command
print("\n[1/3] 🔧 Building PyInstaller command...")

cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--onefile',
    '--name', 'miniZ_MCP_v4.3.0',
    '--distpath', str(OUTPUT_DIR),
    '--workpath', str(BASE_DIR / 'build'),
    '--specpath', str(BASE_DIR),
    '--clean',
    '--noconfirm',
]

# Add hidden imports
for imp in HIDDEN_IMPORTS:
    cmd.extend(['--hidden-import', imp])

# Add data files
for src, dst in DATA_FILES:
    src_path = BASE_DIR / src
    if src_path.exists():
        cmd.extend(['--add-data', f'{src_path};{dst}'])
        print(f"  ✅ Data: {src}")
    else:
        print(f"  ⚠️ Skip (not found): {src}")

# Add icon if exists
icon_path = BASE_DIR / 'icon.ico'
if icon_path.exists():
    cmd.extend(['--icon', str(icon_path)])
    print(f"  ✅ Icon: icon.ico")

# Console mode (show console for debugging)
cmd.append('--console')

# Main script
cmd.append(str(BASE_DIR / 'xiaozhi_final.py'))

print(f"\n[2/3] 🚀 Running PyInstaller...")
print(f"  Command: pyinstaller --onefile xiaozhi_final.py")
print(f"  This may take 2-5 minutes...\n")

# Run build
start_time = datetime.now()
result = subprocess.run(cmd, cwd=str(BASE_DIR))

elapsed = datetime.now() - start_time

if result.returncode == 0:
    exe_path = OUTPUT_DIR / 'miniZ_MCP_v4.3.0.exe'
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"""
╔════════════════════════════════════════════════════════════╗
║                  ✅ BUILD SUCCESS!                          ║
╚════════════════════════════════════════════════════════════╝

📦 Output: {exe_path}
📊 Size: {size_mb:.1f} MB
⏱️ Time: {elapsed.seconds}s

[3/3] 📋 Copy additional files to output...
""")
        
        # Copy additional required files
        files_to_copy = [
            'rag_config.json',
            'knowledge_config.json',
            'xiaozhi_endpoints.json.example',
        ]
        
        for f in files_to_copy:
            src = BASE_DIR / f
            if src.exists():
                import shutil
                shutil.copy(src, OUTPUT_DIR / f)
                print(f"  ✅ Copied: {f}")
        
        # Create example endpoints file
        example_endpoints = {
            "devices": [
                {"name": "Thiết bị 1", "ws_url": "wss://your-xiaozhi-endpoint/mcp"}
            ],
            "active_device": 0
        }
        with open(OUTPUT_DIR / 'xiaozhi_endpoints.json.example', 'w', encoding='utf-8') as f:
            import json
            json.dump(example_endpoints, f, indent=2, ensure_ascii=False)
        
        print(f"""
✅ Done! Run the EXE:
   {exe_path}
""")
    else:
        print("❌ EXE file not found after build!")
else:
    print(f"""
❌ BUILD FAILED!
Exit code: {result.returncode}
Check errors above.
""")

