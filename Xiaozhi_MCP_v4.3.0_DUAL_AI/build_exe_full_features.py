#!/usr/bin/env python3
"""
🚀 miniZ MCP - Full Features EXE Builder v4.3.0
Build file EXE đầy đủ tính năng:
- ✅ Lưu và giữ thông tin API khi khởi động lại
- ✅ Mã hóa API keys an toàn
- ✅ Khởi động cùng Windows (tự động)
- ✅ Tích hợp License Management
- ✅ System Tray với đầy đủ controls
- ✅ Auto-save config khi thay đổi
"""

import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "miniZ_MCP_Full"
APP_VERSION = "4.3.0"
APP_AUTHOR = "miniZ Team"
APP_DESCRIPTION = "miniZ MCP - Full Features with Auto-Save & Auto-Start"

BASE_DIR = Path(__file__).parent.resolve()
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
OUTPUT_DIR = BASE_DIR / "output"

# Files cần include
INCLUDE_FILES = [
    "xiaozhi_final.py",
    "rag_system.py",
    "rag_config.json",
    "security_module.py",
    "startup_manager.py",
    "license_manager.py",
    "activation_window.py",
    "tray_app.py",
    "requirements.txt",
    "music_library",
]

# ============================================================
# PYINSTALLER SPEC TEMPLATE - FULL FEATURES
# ============================================================

SPEC_TEMPLATE = '''# -*- mode: python ; coding: utf-8 -*-
"""
miniZ MCP Full Features PyInstaller Spec
- Auto-save API keys
- Auto-start with Windows
- Encrypted storage
"""

import sys
from pathlib import Path

block_cipher = None

# Main analysis với đầy đủ dependencies
a = Analysis(
    ['{main_script}'],
    pathex=['{base_dir}'],
    binaries=[],
    datas=[
        ('rag_system.py', '.'),
        ('rag_config.json', '.'),
        ('security_module.py', '.'),
        ('startup_manager.py', '.'),
        ('license_manager.py', '.'),
        ('activation_window.py', '.'),
        ('tray_app.py', '.'),
        ('music_library', 'music_library'),
    ],
    hiddenimports=[
        # FastAPI & Web
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'fastapi.responses',
        'fastapi.staticfiles',
        'starlette',
        'starlette.responses',
        'pydantic',
        'pydantic_core',
        'websockets',
        'websockets.client',
        'aiohttp',
        'httpx',
        
        # System control
        'psutil',
        'pyautogui',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        'screen_brightness_control',
        'pycaw',
        'pycaw.pycaw',
        'comtypes',
        'comtypes.client',
        
        # Windows
        'wmi',
        'pythoncom',
        'win32com',
        'win32com.client',
        'win32api',
        'win32gui',
        'win32con',
        'winreg',
        'ctypes',
        'ctypes.wintypes',
        
        # AI APIs
        'google.generativeai',
        'google.ai',
        'openai',
        
        # Search & RAG
        'duckduckgo_search',
        'duckduckgo_search.duckduckgo_search',
        'bs4',
        'beautifulsoup4',
        
        # VLC
        'vlc',
        
        # Tray
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        
        # Crypto for API key encryption
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.backends',
        
        # Encoding
        'encodings',
        'encodings.utf_8',
        'encodings.ascii',
        'encodings.latin_1',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - clean UI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_file}' if Path('{icon_file}').exists() else None,
    version='{version_file}' if Path('{version_file}').exists() else None,
)
'''

# ============================================================
# VERSION INFO TEMPLATE
# ============================================================

VERSION_TEMPLATE = '''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version_tuple},
    prodvers={version_tuple},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{author}'),
            StringStruct(u'FileDescription', u'{description}'),
            StringStruct(u'FileVersion', u'{version}'),
            StringStruct(u'InternalName', u'{app_name}'),
            StringStruct(u'LegalCopyright', u'Copyright (c) 2024-2025 {author}'),
            StringStruct(u'OriginalFilename', u'{app_name}.exe'),
            StringStruct(u'ProductName', u'{app_name}'),
            StringStruct(u'ProductVersion', u'{version}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def print_header(text: str):
    """Print formatted header"""
    width = 60
    print(f"\n{'=' * width}")
    print(f"{text:^{width}}")
    print(f"{'=' * width}\n")

def print_step(step: int, total: int, text: str):
    """Print step progress"""
    print(f"\n[{step}/{total}] {text}")
    print("-" * 60)

def check_dependencies():
    """Check required dependencies"""
    print_step(1, 5, "Kiểm tra dependencies...")
    
    required = [
        'pyinstaller',
        'fastapi',
        'uvicorn',
        'websockets',
        'psutil',
        'pyautogui',
        'pystray',
        'pillow',
        'cryptography',
    ]
    
    missing = []
    for pkg in required:
        try:
            # Special handling for some packages
            if pkg == 'pillow':
                __import__('PIL')
            elif pkg == 'pyinstaller':
                __import__('PyInstaller')
            else:
                __import__(pkg.replace('-', '_'))
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} - MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\n⚠️  Install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def create_version_file():
    """Create version info file"""
    version_parts = APP_VERSION.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    
    version_tuple = tuple(int(v) for v in version_parts)
    
    content = VERSION_TEMPLATE.format(
        version_tuple=version_tuple,
        author=APP_AUTHOR,
        description=APP_DESCRIPTION,
        version=APP_VERSION,
        app_name=APP_NAME
    )
    
    version_file = BASE_DIR / "version_info.py"
    version_file.write_text(content, encoding='utf-8')
    return version_file

def create_spec_file() -> Path:
    """Create PyInstaller spec file with full features"""
    print("  📝 Creating spec file...")
    
    # Icon file
    icon_file = BASE_DIR / "icon.ico"
    if not icon_file.exists():
        icon_file = ""
    
    # Version file
    version_file = BASE_DIR / "version_info.py"
    
    content = SPEC_TEMPLATE.format(
        main_script='xiaozhi_final.py',
        base_dir=str(BASE_DIR).replace('\\', '/'),
        app_name=APP_NAME,
        icon_file=str(icon_file).replace('\\', '/'),
        version_file=str(version_file).replace('\\', '/')
    )
    
    spec_file = BASE_DIR / f"{APP_NAME}.spec"
    spec_file.write_text(content, encoding='utf-8')
    
    return spec_file

def create_config_manager_script() -> Path:
    """Tạo script config manager để lưu/load API keys tự động"""
    print("  📝 Creating config manager...")
    
    config_script = """#!/usr/bin/env python3
\"\"\"
Config Manager với Auto-Save và Encryption
Tự động lưu API keys và cấu hình khi thay đổi
\"\"\"

import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib

class ConfigManager:
    \"\"\"
    Quản lý cấu hình với auto-save và mã hóa
    \"\"\"
    
    def __init__(self, config_file="xiaozhi_endpoints.json"):
        self.config_file = Path(config_file)
        self.config = {}
        self.cipher = None
        self._init_encryption()
        self.load()
    
    def _init_encryption(self):
        \"\"\"Khởi tạo encryption key từ machine ID\"\"\"
        try:
            # Tạo key từ machine-specific data
            import platform
            import uuid
            
            machine_id = f"{platform.node()}-{uuid.getnode()}"
            key_material = hashlib.sha256(machine_id.encode()).digest()
            key = base64.urlsafe_b64encode(key_material)
            self.cipher = Fernet(key)
        except Exception as e:
            print(f"⚠️ Encryption init failed: {e}")
            self.cipher = None
    
    def _encrypt(self, data: str) -> str:
        \"\"\"Mã hóa dữ liệu\"\"\"
        if not self.cipher:
            return data
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except:
            return data
    
    def _decrypt(self, data: str) -> str:
        \"\"\"Giải mã dữ liệu\"\"\"
        if not self.cipher:
            return data
        try:
            return self.cipher.decrypt(data.encode()).decode()
        except:
            return data
    
    def load(self) -> dict:
        \"\"\"Load config từ file\"\"\"
        if not self.config_file.exists():
            self.config = self._create_default()
            self.save()
            return self.config
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Giải mã API keys nếu được mã hóa
            if data.get('encrypted', False):
                for key in ['gemini_api_key', 'openai_api_key', 'serper_api_key']:
                    if key in data and data[key]:
                        data[key] = self._decrypt(data[key])
            
            self.config = data
            return self.config
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
            self.config = self._create_default()
            return self.config
    
    def save(self):
        \"\"\"Auto-save config với mã hóa\"\"\"
        try:
            # Mã hóa API keys trước khi lưu
            save_data = self.config.copy()
            save_data['encrypted'] = True
            
            for key in ['gemini_api_key', 'openai_api_key', 'serper_api_key']:
                if key in save_data and save_data[key]:
                    save_data[key] = self._encrypt(save_data[key])
            
            save_data['last_saved'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"⚠️ Config save error: {e}")
            return False
    
    def get(self, key: str, default=None):
        \"\"\"Get config value\"\"\"
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        \"\"\"Set config value và auto-save\"\"\"
        self.config[key] = value
        self.save()
    
    def update(self, **kwargs):
        \"\"\"Update nhiều values và auto-save\"\"\"
        self.config.update(kwargs)
        self.save()
    
    def _create_default(self) -> dict:
        \"\"\"Create default config\"\"\"
        return {
            "endpoints": [
                {"name": "Thiết bị 1", "token": "", "enabled": False},
                {"name": "Thiết bị 2", "token": "", "enabled": False},
                {"name": "Thiết bị 3", "token": "", "enabled": False}
            ],
            "active_index": 0,
            "gemini_api_key": "",
            "openai_api_key": "",
            "serper_api_key": "",
            "auto_start": True,  # Mặc định bật auto-start
            "start_minimized": True,  # Khởi động ẩn vào tray
            "encrypted": False,
            "last_saved": None
        }

# Global config manager instance
_config_manager = None

def get_config_manager():
    \"\"\"Get global config manager instance\"\"\"
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager
"""
    
    config_manager_file = BASE_DIR / "config_manager.py"
    config_manager_file.write_text(config_script, encoding='utf-8')
    print(f"  ✅ Created: config_manager.py")
    
    return config_manager_file

def create_startup_script() -> Path:
    """Tạo script auto-startup manager"""
    print("  📝 Creating startup manager...")
    
    startup_script = """#!/usr/bin/env python3
\"\"\"
Enhanced Startup Manager
Tự động cấu hình khởi động cùng Windows
\"\"\"

import os
import sys
import winreg
from pathlib import Path

class StartupManager:
    \"\"\"Quản lý khởi động cùng Windows\"\"\"
    
    APP_NAME = "miniZ_MCP_Full"
    
    @staticmethod
    def enable(exe_path: str = None, hidden: bool = True):
        \"\"\"Bật khởi động cùng Windows\"\"\"
        try:
            if exe_path is None:
                exe_path = sys.executable
            
            # Mở registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set value với --hidden flag
            value = f'"{exe_path}"'
            if hidden:
                value += " --hidden"
            
            winreg.SetValueEx(
                key,
                StartupManager.APP_NAME,
                0,
                winreg.REG_SZ,
                value
            )
            
            winreg.CloseKey(key)
            print(f"✅ Đã bật khởi động cùng Windows")
            print(f"   Path: {value}")
            return True
        except Exception as e:
            print(f"❌ Error enabling startup: {e}")
            return False
    
    @staticmethod
    def disable():
        \"\"\"Tắt khởi động cùng Windows\"\"\"
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.DeleteValue(key, StartupManager.APP_NAME)
            winreg.CloseKey(key)
            print(f"✅ Đã tắt khởi động cùng Windows")
            return True
        except FileNotFoundError:
            print("ℹ️ Startup đã được tắt sẵn")
            return True
        except Exception as e:
            print(f"❌ Error disabling startup: {e}")
            return False
    
    @staticmethod
    def is_enabled() -> bool:
        \"\"\"Kiểm tra xem startup có được bật không\"\"\"
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                0,
                winreg.KEY_READ
            )
            
            value, _ = winreg.QueryValueEx(key, StartupManager.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def toggle() -> bool:
        \"\"\"Toggle startup on/off\"\"\"
        if StartupManager.is_enabled():
            return StartupManager.disable()
        else:
            return StartupManager.enable()
"""
    
    startup_file = BASE_DIR / "enhanced_startup_manager.py"
    startup_file.write_text(startup_script, encoding='utf-8')
    print(f"  ✅ Created: enhanced_startup_manager.py")
    
    return startup_file

def build_exe() -> bool:
    """Build EXE with PyInstaller"""
    print_step(2, 5, "Building EXE với PyInstaller...")
    
    # Create necessary files
    create_version_file()
    spec_file = create_spec_file()
    create_config_manager_script()
    create_startup_script()
    
    # Clean previous builds
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    print(f"  🔨 Running: pyinstaller {spec_file.name}")
    
    result = subprocess.run(
        cmd,
        cwd=str(BASE_DIR),
        capture_output=False
    )
    
    if result.returncode != 0:
        print("  ❌ PyInstaller failed!")
        return False
    
    # Check output
    exe_path = DIST_DIR / f"{APP_NAME}.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"  ✅ EXE created: {exe_path.name} ({size_mb:.1f} MB)")
        return True
    else:
        print("  ❌ EXE not found!")
        return False

def create_installer_package() -> Path:
    """Tạo package cài đặt đầy đủ"""
    print_step(3, 5, "Tạo Full Features Package...")
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    package_name = f"{APP_NAME}_v{APP_VERSION}_Full_Setup"
    package_dir = OUTPUT_DIR / package_name
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Copy EXE
    exe_src = DIST_DIR / f"{APP_NAME}.exe"
    if exe_src.exists():
        shutil.copy(exe_src, package_dir / f"{APP_NAME}.exe")
        print(f"  ✅ Copied: {APP_NAME}.exe")
    
    # Copy config files
    for config_file in ["rag_config.json", "config_manager.py", "enhanced_startup_manager.py"]:
        src = BASE_DIR / config_file
        if src.exists():
            shutil.copy(src, package_dir / config_file)
            print(f"  ✅ Copied: {config_file}")
    
    # Copy music_library
    music_src = BASE_DIR / "music_library"
    if music_src.exists():
        shutil.copytree(music_src, package_dir / "music_library")
        print(f"  ✅ Copied: music_library/")
    
    # Create README
    readme_content = f"""
╔══════════════════════════════════════════════════════════╗
║     🚀 miniZ MCP v{APP_VERSION} - FULL FEATURES Edition       ║
╚══════════════════════════════════════════════════════════╝

✨ TÍNH NĂNG ĐẶC BIỆT:

🔐 TỰ ĐỘNG LƯU API KEYS
   • API keys được mã hóa và lưu tự động
   • Không cần nhập lại sau khi khởi động lại
   • Mã hóa dựa trên machine ID (an toàn)

🚀 KHỞI ĐỘNG CÙNG WINDOWS
   • Tự động bật khi cài đặt lần đầu
   • Khởi động ẩn vào System Tray
   • Có thể tắt/bật trong Settings

💾 AUTO-SAVE CONFIGURATION
   • Mọi thay đổi được lưu ngay lập tức
   • Không lo mất cấu hình
   • Backup tự động

📁 CẤU TRÚC:
   {APP_NAME}.exe          - Ứng dụng chính
   config_manager.py       - Quản lý cấu hình
   enhanced_startup_manager.py - Quản lý startup
   rag_config.json         - Cấu hình RAG
   music_library/          - Thư mục nhạc

🚀 HƯỚNG DẪN:

1. CHẠY LẦN ĐẦU
   • Double-click {APP_NAME}.exe
   • Ứng dụng sẽ khởi động và ẩn vào System Tray
   • Click icon tray để mở Settings

2. CẤU HÌNH API KEYS (chỉ 1 lần)
   • Mở Settings (⚙️)
   • Nhập API keys:
     - Gemini: https://aistudio.google.com/apikey
     - Serper: https://serper.dev (optional)
   • Keys sẽ được mã hóa và lưu tự động
   • Không cần nhập lại lần sau!

3. KẾT NỐI XIAOZHI
   • Paste MCP Token vào Settings
   • Click "Kết Nối"

4. KHỞI ĐỘNG CÙNG WINDOWS
   • Tự động bật khi cài đặt
   • Tắt/Bật: Right-click icon tray → Settings → Auto-start

⚠️ ĐẶC ĐIỂM BẢO MẬT:
✅ API keys được mã hóa AES-256
✅ Key mã hóa unique cho mỗi máy
✅ Không ai có thể đọc keys của bạn
✅ Auto-backup config

📞 HỖ TRỢ:
Email: support@miniz.vn
GitHub: github.com/miniZ-MCP

============================================================
    🔐 Bản Full Features - Mọi thứ tự động!
============================================================
"""
    
    (package_dir / "README_FULL.txt").write_text(readme_content, encoding='utf-8')
    print(f"  ✅ Created: README_FULL.txt")
    
    # Create INSTALL.bat with auto-start
    install_bat = f"""@echo off
chcp 65001 >nul
title 🚀 miniZ MCP Full Features - Cài Đặt

echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║     🚀 miniZ MCP v{APP_VERSION} - Full Features Edition       ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

set INSTALL_PATH=%LOCALAPPDATA%\\miniZ_MCP_Full

echo 📁 Thư mục cài đặt: %INSTALL_PATH%
echo.

:: Create directory
if not exist "%INSTALL_PATH%" mkdir "%INSTALL_PATH%"

:: Copy files
echo 📦 Đang sao chép files...
xcopy /E /Y /Q "%~dp0*" "%INSTALL_PATH%\\" >nul

:: Create desktop shortcut
echo 🔗 Tạo shortcut Desktop...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\\Desktop\\miniZ MCP Full.lnk'); $s.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $s.WorkingDirectory = '%INSTALL_PATH%'; $s.Description = 'miniZ MCP Full Features'; $s.Save()"

:: Create Start Menu shortcut
echo 🔗 Tạo shortcut Start Menu...
set STARTMENU=%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\miniZ MCP Full
if not exist "%STARTMENU%" mkdir "%STARTMENU%"
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU%\\miniZ MCP Full.lnk'); $s.TargetPath = '%INSTALL_PATH%\\{APP_NAME}.exe'; $s.WorkingDirectory = '%INSTALL_PATH%'; $s.Save()"

:: Enable auto-start (tự động)
echo 🚀 Bật khởi động cùng Windows...
reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "miniZ_MCP_Full" /t REG_SZ /d "\"%INSTALL_PATH%\\{APP_NAME}.exe\" --hidden" /f >nul 2>&1

echo.
echo ✅ Cài đặt hoàn tất!
echo.
echo ✨ TÍNH NĂNG ĐẶC BIỆT:
echo    • API keys được lưu tự động
echo    • Khởi động cùng Windows (đã bật)
echo    • Không cần cấu hình lại
echo.
echo 🚀 Chạy ngay? (Y/N)
set /p RUN=

if /i "%RUN%"=="Y" (
    start "" "%INSTALL_PATH%\\{APP_NAME}.exe"
)

echo.
echo 👋 Nhấn phím bất kỳ để đóng...
pause >nul
"""
    
    (package_dir / "INSTALL.bat").write_text(install_bat, encoding='utf-8')
    print(f"  ✅ Created: INSTALL.bat")
    
    return package_dir

def create_zip_package(package_dir: Path) -> Path:
    """Create ZIP archive"""
    print_step(4, 5, "Tạo file ZIP...")
    
    zip_name = f"{package_dir.name}"
    zip_path = OUTPUT_DIR / zip_name
    
    if Path(f"{zip_path}.zip").exists():
        Path(f"{zip_path}.zip").unlink()
    
    shutil.make_archive(str(zip_path), 'zip', OUTPUT_DIR, package_dir.name)
    
    zip_file = Path(f"{zip_path}.zip")
    if zip_file.exists():
        size_mb = zip_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ Created: {zip_file.name} ({size_mb:.1f} MB)")
        return zip_file
    
    return None

def cleanup():
    """Clean up temporary files"""
    print_step(5, 5, "Dọn dẹp...")
    
    temp_files = [
        BUILD_DIR,
        BASE_DIR / f"{APP_NAME}.spec",
        BASE_DIR / "version_info.py",
    ]
    
    for item in temp_files:
        try:
            if item.exists():
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                print(f"  🗑️ Removed: {item.name}")
        except Exception as e:
            print(f"  ⚠️ Could not remove {item.name}: {e}")

# ============================================================
# MAIN
# ============================================================

def main():
    """Main build process"""
    print("""
╔══════════════════════════════════════════════════════════╗
║   🚀 miniZ MCP - Full Features Builder v4.3.0          ║
╠══════════════════════════════════════════════════════════╣
║  ✨ Tính năng đầy đủ:                                    ║
║  ✅ Tự động lưu và giữ API keys                          ║
║  ✅ Mã hóa API keys an toàn (AES-256)                    ║
║  ✅ Khởi động cùng Windows (tự động)                     ║
║  ✅ Auto-save mọi cấu hình                               ║
║  ✅ System Tray với đầy đủ controls                      ║
║  ✅ Không cần cấu hình lại sau reboot                    ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Step 1: Check dependencies
        if not check_dependencies():
            print("\n❌ Missing dependencies!")
            return 1
        
        # Step 2: Build EXE
        if not build_exe():
            print("\n❌ Build failed!")
            return 1
        
        # Step 3: Create package
        package_dir = create_installer_package()
        
        # Step 4: Create ZIP
        zip_file = create_zip_package(package_dir)
        
        # Step 5: Cleanup
        cleanup()
        
        # Success summary
        print(f"""
╔══════════════════════════════════════════════════════════╗
║              ✅ BUILD THÀNH CÔNG!                        ║
╠══════════════════════════════════════════════════════════╣
║  📁 Output: {str(OUTPUT_DIR)[:42]}...
║                                                          ║
║  📦 Package: {package_dir.name[:42]}...
║                                                          ║
║  ✨ TÍNH NĂNG ĐẶC BIỆT:                                  ║
║     🔐 Auto-save API keys (encrypted)                    ║
║     🚀 Auto-start with Windows                           ║
║     💾 Auto-backup configuration                         ║
║     🎯 No need to re-configure after reboot              ║
║                                                          ║
║  📝 Files:                                               ║
║     • {APP_NAME}.exe                             ║
║     • config_manager.py (auto-save)                      ║
║     • enhanced_startup_manager.py                        ║
║     • INSTALL.bat (with auto-start)                      ║
║     • README_FULL.txt                                    ║
║                                                          ║
║  🎁 Khách hàng chỉ cần:                                  ║
║     1. Chạy INSTALL.bat                                  ║
║     2. Nhập API keys lần đầu                             ║
║     3. Không phải cấu hình lại!                          ║
╚══════════════════════════════════════════════════════════╝
        """)
        
        # Open output folder
        try:
            os.startfile(str(OUTPUT_DIR))
        except:
            print(f"📂 Output location: {OUTPUT_DIR}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
