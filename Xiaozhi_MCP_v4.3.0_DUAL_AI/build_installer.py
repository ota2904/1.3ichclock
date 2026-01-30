#!/usr/bin/env python3
"""
🚀 miniZ MCP Installer Builder
Tạo file cài đặt EXE với đầy đủ tính năng:
- Khởi động cùng Windows
- Chạy ngầm (system tray)
- Bảo mật API keys
- Tự động cập nhật

Author: miniZ Team
Version: 4.3.0
"""

import os
import sys
import json
import base64
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "miniZ_MCP"
APP_VERSION = "4.3.0"
APP_AUTHOR = "miniZ Team"
APP_DESCRIPTION = "miniZ MCP - Điều khiển máy tính bằng AI"
MAIN_SCRIPT = "xiaozhi_final.py"
ICON_FILE = "miniz_icon.ico"

# Directories
BASE_DIR = Path(__file__).parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
INSTALLER_DIR = BASE_DIR / "installer"

# ============================================================
# ENCRYPTION KEY (for API keys protection)
# ============================================================

def generate_machine_key():
    """Generate encryption key based on machine hardware ID"""
    import hashlib
    import uuid
    
    # Get machine-specific identifiers
    machine_id = str(uuid.getnode())  # MAC address as integer
    
    # Create a hash
    key = hashlib.sha256(f"miniZ_MCP_{machine_id}".encode()).hexdigest()[:32]
    return key

def encrypt_api_key(api_key: str, machine_key: str) -> str:
    """Encrypt API key using XOR with machine key"""
    if not api_key:
        return ""
    
    encrypted = ""
    for i, char in enumerate(api_key):
        key_char = machine_key[i % len(machine_key)]
        encrypted_char = chr(ord(char) ^ ord(key_char))
        encrypted += encrypted_char
    
    return base64.b64encode(encrypted.encode('latin-1')).decode('ascii')

def decrypt_api_key(encrypted: str, machine_key: str) -> str:
    """Decrypt API key"""
    if not encrypted:
        return ""
    
    try:
        decoded = base64.b64decode(encrypted.encode('ascii')).decode('latin-1')
        decrypted = ""
        for i, char in enumerate(decoded):
            key_char = machine_key[i % len(machine_key)]
            decrypted_char = chr(ord(char) ^ ord(key_char))
            decrypted += decrypted_char
        return decrypted
    except:
        return ""

# ============================================================
# STARTUP MANAGER
# ============================================================

STARTUP_MANAGER_CODE = '''
"""
miniZ MCP Startup Manager
Quản lý khởi động cùng Windows
"""

import os
import sys
import winreg
import ctypes
from pathlib import Path

APP_NAME = "miniZ_MCP"

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_startup_registry_key():
    """Get Windows startup registry key"""
    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
        0,
        winreg.KEY_ALL_ACCESS
    )

def enable_startup(exe_path: str, run_hidden: bool = True):
    """Enable startup with Windows"""
    try:
        key = get_startup_registry_key()
        
        # Add --hidden flag for background mode
        value = f'"{exe_path}"'
        if run_hidden:
            value += " --hidden"
        
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error enabling startup: {e}")
        return False

def disable_startup():
    """Disable startup with Windows"""
    try:
        key = get_startup_registry_key()
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return True  # Already disabled
    except Exception as e:
        print(f"Error disabling startup: {e}")
        return False

def is_startup_enabled():
    """Check if startup is enabled"""
    try:
        key = get_startup_registry_key()
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False

def toggle_startup(exe_path: str = None):
    """Toggle startup on/off"""
    if is_startup_enabled():
        return disable_startup()
    else:
        if exe_path is None:
            exe_path = sys.executable
        return enable_startup(exe_path)

if __name__ == "__main__":
    print(f"Startup enabled: {is_startup_enabled()}")
'''

# ============================================================
# SYSTEM TRAY WRAPPER
# ============================================================

TRAY_WRAPPER_CODE = '''
"""
miniZ MCP System Tray
Chạy ngầm trong system tray với menu context
"""

import os
import sys
import threading
import webbrowser
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import pystray
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("Warning: pystray or PIL not installed. System tray disabled.")

from startup_manager import enable_startup, disable_startup, is_startup_enabled

APP_NAME = "miniZ MCP"
APP_PORT = 8000

def create_icon_image():
    """Create a simple icon for system tray"""
    # Create a gradient icon
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), '#667eea')
    draw = ImageDraw.Draw(image)
    
    # Draw gradient effect
    for y in range(height):
        ratio = y / height
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        for x in range(width):
            draw.point((x, y), fill=(r, g, b))
    
    # Draw "MZ" text
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((width//2, height//2), "MZ", fill='white', anchor='mm', font=font)
    
    return image

def open_dashboard():
    """Open web dashboard in browser"""
    webbrowser.open(f"http://localhost:{APP_PORT}")

def toggle_startup_menu(icon, item):
    """Toggle startup setting from menu"""
    if is_startup_enabled():
        disable_startup()
        icon.notify("Đã tắt khởi động cùng Windows", APP_NAME)
    else:
        exe_path = sys.executable
        enable_startup(exe_path, run_hidden=True)
        icon.notify("Đã bật khởi động cùng Windows", APP_NAME)

def exit_app(icon, item):
    """Exit application"""
    icon.stop()
    os._exit(0)

def run_server():
    """Run the main server in background"""
    import xiaozhi_final
    # Server will start automatically

def run_tray():
    """Run system tray icon"""
    if not TRAY_AVAILABLE:
        print("System tray not available. Running in foreground mode.")
        run_server()
        return
    
    # Create menu
    menu = pystray.Menu(
        pystray.MenuItem("🌐 Mở Dashboard", open_dashboard, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            "🚀 Khởi động cùng Windows",
            toggle_startup_menu,
            checked=lambda item: is_startup_enabled()
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Thoát", exit_app)
    )
    
    # Create icon
    icon = pystray.Icon(
        APP_NAME,
        create_icon_image(),
        f"{APP_NAME} v4.3.0",
        menu
    )
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Show notification
    icon.notify(f"{APP_NAME} đang chạy ngầm", APP_NAME)
    
    # Run tray icon
    icon.run()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hidden", action="store_true", help="Run in background mode")
    args = parser.parse_args()
    
    if args.hidden or "--hidden" in sys.argv:
        # Background mode with system tray
        run_tray()
    else:
        # Normal mode - just run server
        run_server()
'''

# ============================================================
# PYINSTALLER SPEC FILE
# ============================================================

def generate_spec_file():
    """Generate PyInstaller spec file"""
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
"""
miniZ MCP PyInstaller Spec File
Auto-generated by build_installer.py
"""

import sys
from pathlib import Path

block_cipher = None

# Collect all Python files
a = Analysis(
    ['tray_app.py'],
    pathex=['{BASE_DIR}'],
    binaries=[],
    datas=[
        ('rag_system.py', '.'),
        ('xiaozhi_final.py', '.'),
        ('rag_config.json', '.'),
        ('music_library', 'music_library'),
    ],
    hiddenimports=[
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
        'starlette',
        'pydantic',
        'websockets',
        'aiohttp',
        'httpx',
        'psutil',
        'pyautogui',
        'pynput',
        'screen_brightness_control',
        'pycaw',
        'comtypes',
        'wmi',
        'pythoncom',
        'win32com',
        'win32api',
        'win32gui',
        'win32con',
        'winreg',
        'ctypes',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'google.generativeai',
        'openai',
        'duckduckgo_search',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
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
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{ICON_FILE}' if Path('{ICON_FILE}').exists() else None,
    version='version_info.txt',
)
'''
    return spec_content

# ============================================================
# VERSION INFO FILE
# ============================================================

def generate_version_info():
    """Generate Windows version info file"""
    
    version_parts = APP_VERSION.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    
    version_tuple = tuple(int(v) for v in version_parts[:4])
    
    content = f'''# UTF-8
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
            StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
            StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
            StringStruct(u'FileVersion', u'{APP_VERSION}'),
            StringStruct(u'InternalName', u'{APP_NAME}'),
            StringStruct(u'LegalCopyright', u'Copyright (c) 2024 {APP_AUTHOR}'),
            StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
            StringStruct(u'ProductName', u'{APP_NAME}'),
            StringStruct(u'ProductVersion', u'{APP_VERSION}'),
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    return content

# ============================================================
# INNO SETUP SCRIPT (for installer)
# ============================================================

def generate_inno_script():
    """Generate Inno Setup script for professional installer"""
    
    script = f'''
; miniZ MCP Installer Script
; Generated by build_installer.py

#define MyAppName "{APP_NAME}"
#define MyAppVersion "{APP_VERSION}"
#define MyAppPublisher "{APP_AUTHOR}"
#define MyAppURL "https://github.com/miniZ-MCP"
#define MyAppExeName "{APP_NAME}.exe"

[Setup]
AppId={{{{D7A8B9C0-1234-5678-9ABC-DEF012345678}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=miniZ_MCP_Setup_v{APP_VERSION}
SetupIconFile=miniz_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "vietnamese"; MessagesFile: "compiler:Languages\\Vietnamese.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "startup"; Description: "Khởi động cùng Windows"; GroupDescription: "Tùy chọn khởi động"

[Files]
Source: "dist\\{{#MyAppExeName}}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "rag_config.json"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "music_library\\*"; DestDir: "{{app}}\\music_library"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{{app}}"; Flags: ignoreversion

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon
Name: "{{userappdata}}\\Microsoft\\Internet Explorer\\Quick Launch\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: quicklaunchicon

[Registry]
; Enable startup if user selected it
Root: HKCU; Subkey: "Software\\Microsoft\\Windows\\CurrentVersion\\Run"; ValueType: string; ValueName: "{{#MyAppName}}"; ValueData: """{{app}}\\{{#MyAppExeName}}"" --hidden"; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "Khởi động {{#MyAppName}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Post-installation tasks
  end;
end;
'''
    return script

# ============================================================
# BUILD FUNCTIONS
# ============================================================

def check_dependencies():
    """Check if required packages are installed"""
    required = ['pyinstaller', 'pystray', 'Pillow']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.lower().replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"⚠️ Missing packages: {', '.join(missing)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, check=True)
    
    return True

def create_support_files():
    """Create support files (startup_manager, tray_app)"""
    
    # Create startup_manager.py
    startup_path = BASE_DIR / "startup_manager.py"
    with open(startup_path, 'w', encoding='utf-8') as f:
        f.write(STARTUP_MANAGER_CODE)
    print(f"✅ Created: {startup_path}")
    
    # Create tray_app.py
    tray_path = BASE_DIR / "tray_app.py"
    with open(tray_path, 'w', encoding='utf-8') as f:
        f.write(TRAY_WRAPPER_CODE)
    print(f"✅ Created: {tray_path}")
    
    # Create version_info.txt
    version_path = BASE_DIR / "version_info.txt"
    with open(version_path, 'w', encoding='utf-8') as f:
        f.write(generate_version_info())
    print(f"✅ Created: {version_path}")
    
    # Create spec file
    spec_path = BASE_DIR / f"{APP_NAME}.spec"
    with open(spec_path, 'w', encoding='utf-8') as f:
        f.write(generate_spec_file())
    print(f"✅ Created: {spec_path}")
    
    # Create Inno Setup script
    inno_path = BASE_DIR / "setup.iss"
    with open(inno_path, 'w', encoding='utf-8') as f:
        f.write(generate_inno_script())
    print(f"✅ Created: {inno_path}")

def build_exe():
    """Build EXE using PyInstaller"""
    print("\n" + "="*60)
    print("🔨 Building EXE with PyInstaller...")
    print("="*60)
    
    spec_file = BASE_DIR / f"{APP_NAME}.spec"
    
    if not spec_file.exists():
        print("❌ Spec file not found. Creating...")
        create_support_files()
    
    # Run PyInstaller
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    
    if result.returncode == 0:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"\n✅ Build successful!")
            print(f"📦 EXE: {exe_path}")
            print(f"📏 Size: {size_mb:.2f} MB")
            return True
    
    print("❌ Build failed!")
    return False

def create_portable_zip():
    """Create portable ZIP package"""
    print("\n" + "="*60)
    print("📦 Creating portable ZIP package...")
    print("="*60)
    
    zip_name = f"miniZ_MCP_v{APP_VERSION}_Portable"
    zip_path = INSTALLER_DIR / zip_name
    
    # Create installer directory
    INSTALLER_DIR.mkdir(exist_ok=True)
    
    # Files to include
    files_to_include = [
        'xiaozhi_final.py',
        'rag_system.py',
        'rag_config.json',
        'startup_manager.py',
        'tray_app.py',
        'requirements.txt',
        'README.md',
        'LICENSE',
        'QUICKSTART.md',
        'START.bat',
        'INSTALL.bat',
    ]
    
    # Create portable package
    shutil.make_archive(str(zip_path), 'zip', BASE_DIR)
    print(f"✅ Created: {zip_path}.zip")
    
    return True

def main():
    """Main build process"""
    print("""
╔══════════════════════════════════════════════════════════╗
║         🚀 miniZ MCP Installer Builder v4.3.0            ║
╠══════════════════════════════════════════════════════════╣
║  1. Check dependencies                                    ║
║  2. Create support files                                  ║
║  3. Build EXE with PyInstaller                           ║
║  4. Create Inno Setup installer (optional)               ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check dependencies
    print("\n[1/4] Checking dependencies...")
    check_dependencies()
    
    # Step 2: Create support files
    print("\n[2/4] Creating support files...")
    create_support_files()
    
    # Step 3: Build EXE
    print("\n[3/4] Building EXE...")
    if not build_exe():
        print("❌ Build failed. Please check errors above.")
        return 1
    
    # Step 4: Create portable package
    print("\n[4/4] Creating portable package...")
    create_portable_zip()
    
    print("""
╔══════════════════════════════════════════════════════════╗
║                    ✅ BUILD COMPLETE!                     ║
╠══════════════════════════════════════════════════════════╣
║  📁 Output files:                                         ║
║     • dist/miniZ_MCP.exe          - Standalone EXE        ║
║     • installer/miniZ_MCP_*.zip   - Portable package      ║
║     • setup.iss                   - Inno Setup script     ║
║                                                           ║
║  🚀 To create full installer:                             ║
║     1. Install Inno Setup from jrsoftware.org            ║
║     2. Open setup.iss with Inno Setup                    ║
║     3. Click Build > Compile                              ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
