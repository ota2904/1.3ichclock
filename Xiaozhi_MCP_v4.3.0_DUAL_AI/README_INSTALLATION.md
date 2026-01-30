# 📦 HƯỚNG DẪN CÀI ĐẶT & BUILD EXE - miniZ MCP v4.3.0

## 🎯 Tổng quan

Hướng dẫn đầy đủ về cài đặt và tạo file EXE standalone cho **miniZ MCP v4.3.0 Professional Edition**.

---

## 🚀 PHƯƠNG PHÁP 1: CÀI ĐẶT NHANH (Recommended)

### **Cách 1: Chạy INSTALL.bat**

```batch
# Double-click hoặc chạy từ CMD
INSTALL.bat
```

**✅ Tự động:**
- Kiểm tra Python 3.11+
- Cài đặt pip dependencies
- Tạo config file
- Khởi động server

**⏱️ Thời gian:** ~2-3 phút

---

### **Cách 2: Manual Installation**

#### **Bước 1: Cài Python**
```
📥 Download: https://python.org/downloads
✅ Phiên bản: Python 3.11 hoặc mới hơn
⚠️  LƯU Ý: Tích "Add Python to PATH"
```

#### **Bước 2: Cài dependencies**
```bash
pip install -r requirements.txt
```

#### **Bước 3: Cấu hình**
```bash
# Copy file config mẫu
copy xiaozhi_endpoints.json.example xiaozhi_endpoints.json

# Sửa file và thêm token
notepad xiaozhi_endpoints.json
```

#### **Bước 4: Khởi động**
```bash
# Phương pháp 1: Batch file
START.bat

# Phương pháp 2: Python trực tiếp
python xiaozhi_final.py

# Phương pháp 3: Hidden mode
START_HIDDEN.bat
```

---

## 🔨 PHƯƠNG PHÁP 2: BUILD FILE EXE

### **Option A: Quick Build (Recommended)**

```batch
# Chạy build script
BUILD_EXE.bat
```

**📊 Output:**
- `dist\miniZ_MCP.exe` - Main executable
- `dist\_internal\` - Dependencies
- Size: ~150-200 MB

---

### **Option B: Custom Build với PyInstaller**

#### **1. Cài đặt PyInstaller**
```bash
pip install pyinstaller pystray Pillow pywin32
```

#### **2. Build với spec file**

**File: `miniz_mcp.spec`**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['xiaozhi_final.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('xiaozhi_endpoints.json', '.'),
        ('SMART_ANALYZER_GUIDE.md', '.'),
        ('music_library', 'music_library'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'websockets',
        'psutil',
        'pyautogui',
        'pyperclip',
        'vlc',
        'PIL',
        'pystray',
    ],
    hookspath=[],
    hooksconfig={},
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
    [],
    exclude_binaries=True,
    name='miniZ_MCP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Set False để ẩn console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='miniz_icon.ico',  # Nếu có
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='miniZ_MCP',
)
```

#### **3. Build command**
```bash
# Build với spec file
pyinstaller miniz_mcp.spec

# Hoặc build trực tiếp (onefile)
pyinstaller --onefile ^
  --name miniZ_MCP ^
  --add-data "requirements.txt;." ^
  --add-data "xiaozhi_endpoints.json;." ^
  --hidden-import fastapi ^
  --hidden-import uvicorn ^
  --hidden-import websockets ^
  --icon miniz_icon.ico ^
  xiaozhi_final.py
```

---

### **Option C: Build với Auto Installer**

#### **1. Chạy build script**
```bash
python build_installer.py
```

**🎯 Tính năng tự động:**
- ✅ Detect platform (Windows/Linux/Mac)
- ✅ Create system tray wrapper
- ✅ Auto-startup registry
- ✅ Encrypt API keys
- ✅ Bundle tất cả dependencies

#### **2. Config trong build_installer.py**
```python
# Version & metadata
APP_VERSION = "4.3.0"
APP_NAME = "miniZ_MCP"

# Build options
BUILD_ONEFILE = True  # Single EXE
INCLUDE_TRAY = True   # System tray
ENCRYPT_KEYS = True   # API key encryption
AUTO_STARTUP = True   # Windows startup
```

---

## 🎨 CUSTOM BUILD OPTIONS

### **1. Console vs Windowed**

**Console Mode (Default):**
```bash
pyinstaller --console xiaozhi_final.py
```
- ✅ Hiện terminal window
- ✅ Dễ debug
- ✅ Xem logs real-time

**Windowed Mode (Production):**
```bash
pyinstaller --windowed --noconsole xiaozhi_final.py
```
- ✅ Chạy ngầm hoàn toàn
- ✅ Chỉ hiện system tray
- ❌ Khó debug nếu có lỗi

---

### **2. Single File vs Folder**

**One Folder (Faster startup):**
```bash
pyinstaller --onedir xiaozhi_final.py
```
- ✅ Khởi động nhanh hơn
- ✅ Dễ update từng file
- ❌ Nhiều files (~200)

**One File (Portable):**
```bash
pyinstaller --onefile xiaozhi_final.py
```
- ✅ Chỉ 1 file EXE duy nhất
- ✅ Dễ chia sẻ
- ❌ Khởi động chậm hơn (unpack temp)

---

### **3. UPX Compression**

```bash
# Enable UPX (giảm size 30-40%)
pyinstaller --upx-dir=/path/to/upx xiaozhi_final.py

# Exclude specific files from UPX
pyinstaller --upx-exclude vcruntime140.dll xiaozhi_final.py
```

**📥 Download UPX:** https://upx.github.io/

---

### **4. Icon Customization**

```bash
# Windows
pyinstaller --icon=miniz_icon.ico xiaozhi_final.py

# Mac
pyinstaller --icon=miniz_icon.icns xiaozhi_final.py

# Linux (no icon support)
```

**🎨 Tạo icon:**
- Tool: GIMP, Photoshop, IcoFX
- Format: 256x256 PNG → ICO
- Multi-resolution: 16x16, 32x32, 48x48, 256x256

---

## 🔐 SECURITY & OPTIMIZATION

### **1. Encrypt Sensitive Data**

**API Keys:**
```python
# In build_installer.py
ENCRYPT_KEYS = True

# Machine-specific encryption
def encrypt_api_key(key):
    import hashlib, uuid
    machine_id = str(uuid.getnode())
    cipher_key = hashlib.sha256(machine_id.encode()).hexdigest()
    # XOR encryption...
```

**Config Files:**
```python
# Obfuscate config
import base64, zlib

def protect_config(data):
    compressed = zlib.compress(json.dumps(data).encode())
    return base64.b64encode(compressed).decode()
```

---

### **2. Code Obfuscation**

**PyArmor:**
```bash
pip install pyarmor

# Obfuscate code
pyarmor obfuscate xiaozhi_final.py

# Build với obfuscated code
pyinstaller dist/xiaozhi_final.py
```

---

### **3. Anti-Virus False Positives**

**Giảm detection rate:**

1. **Sign EXE với certificate:**
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com miniZ_MCP.exe
```

2. **Submit to VirusTotal:**
- Upload lần đầu sẽ bị flag
- Sau vài ngày sẽ được whitelist

3. **Exclude from Windows Defender:**
```powershell
Add-MpPreference -ExclusionPath "C:\Path\To\miniZ_MCP.exe"
```

---

## 🌐 MULTI-PLATFORM BUILD

### **Windows**
```bash
# Build trên Windows
BUILD_EXE.bat

# Output
dist\miniZ_MCP.exe
```

### **Linux**
```bash
# Install dependencies
sudo apt install python3-dev libffi-dev

# Build
pyinstaller --onefile xiaozhi_final.py

# Output
dist/miniZ_MCP
```

### **macOS**
```bash
# Install via Homebrew
brew install python upx

# Build
pyinstaller --onefile --windowed xiaozhi_final.py

# Output
dist/miniZ_MCP.app
```

---

## 📦 DISTRIBUTION

### **Option 1: ZIP Package**

```batch
# Create package
CREATE_PACKAGE.bat
```

**📁 Cấu trúc:**
```
miniZ_MCP_v4.3.0_Portable.zip
├── miniZ_MCP.exe
├── README.md
├── QUICKSTART.md
├── requirements.txt
├── xiaozhi_endpoints.json.example
└── music_library/
```

---

### **Option 2: Inno Setup Installer**

**1. Cài Inno Setup:**
```
📥 Download: https://jrsoftware.org/isinfo.php
```

**2. Create script (`installer.iss`):**
```iss
[Setup]
AppName=miniZ MCP
AppVersion=4.3.0
DefaultDirName={pf}\miniZ_MCP
DefaultGroupName=miniZ MCP
OutputDir=installer
OutputBaseFilename=miniZ_MCP_Setup_v4.3.0

[Files]
Source: "dist\miniZ_MCP.exe"; DestDir: "{app}"
Source: "dist\_internal\*"; DestDir: "{app}\_internal"; Flags: recursesubdirs
Source: "README.md"; DestDir: "{app}"

[Icons]
Name: "{group}\miniZ MCP"; Filename: "{app}\miniZ_MCP.exe"
Name: "{autodesktop}\miniZ MCP"; Filename: "{app}\miniZ_MCP.exe"

[Run]
Filename: "{app}\miniZ_MCP.exe"; Description: "Launch miniZ MCP"; Flags: postinstall nowait
```

**3. Build installer:**
```bash
BUILD_INNO_INSTALLER.bat
```

---

### **Option 3: NSIS Installer**

```nsis
!define APP_NAME "miniZ MCP"
!define APP_VERSION "4.3.0"

OutFile "miniZ_MCP_Setup_v4.3.0.exe"
InstallDir "$PROGRAMFILES\miniZ_MCP"

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File "dist\miniZ_MCP.exe"
  File /r "dist\_internal"
  
  CreateShortcut "$DESKTOP\miniZ MCP.lnk" "$INSTDIR\miniZ_MCP.exe"
SectionEnd
```

---

## 🧪 TESTING

### **1. Test Local EXE**
```bash
# Run from dist folder
cd dist
miniZ_MCP.exe

# Test với arguments
miniZ_MCP.exe --hidden
miniZ_MCP.exe --port 8080
```

### **2. Test Auto-Startup**
```batch
# Enable startup
dist\miniZ_MCP.exe --enable-startup

# Check registry
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v miniZ_MCP

# Disable startup
dist\miniZ_MCP.exe --disable-startup
```

### **3. Test System Tray**
```bash
# Run in tray mode
miniZ_MCP.exe --tray

# Right-click tray icon should show:
# • Open Dashboard
# • Settings
# • Exit
```

---

## 🐛 TROUBLESHOOTING

### **Issue 1: "Python not found"**
```bash
# Add Python to PATH
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"

# Verify
python --version
```

---

### **Issue 2: "Module not found" in EXE**
```bash
# Add hidden import
pyinstaller --hidden-import missing_module xiaozhi_final.py

# Or in spec file
hiddenimports=['missing_module']
```

---

### **Issue 3: EXE quá lớn (>200 MB)**
```bash
# Solutions:
1. Use --onedir instead of --onefile
2. Enable UPX compression
3. Exclude unused modules:
   pyinstaller --exclude-module matplotlib xiaozhi_final.py
```

---

### **Issue 4: Antivirus blocks EXE**
```
Solutions:
1. Sign EXE với code signing certificate
2. Submit to VirusTotal
3. Add exclusion trong Windows Defender
4. Use virtual environment để clean build
```

---

### **Issue 5: "Access denied" khi enable startup**
```bash
# Run as Administrator
Right-click BUILD_EXE.bat → Run as Administrator

# Or use Task Scheduler instead of registry
```

---

## 📊 BUILD COMPARISON

| Feature | Portable | One-File EXE | Installer |
|---------|----------|--------------|-----------|
| **Size** | ~5 MB | ~150 MB | ~160 MB |
| **Startup** | Fast | Medium | Fast |
| **Install** | None | None | Required |
| **Portable** | ✅ | ✅ | ❌ |
| **Updates** | Easy | Medium | Auto |
| **Professional** | ❌ | ✅ | ✅✅ |

---

## 🎯 RECOMMENDED WORKFLOW

### **For Development:**
```bash
1. Use INSTALL.bat
2. Run START.bat
3. Edit code
4. Restart server
```

### **For Testing:**
```bash
1. BUILD_EXE.bat
2. Test dist\miniZ_MCP.exe
3. Verify all features
```

### **For Distribution:**
```bash
1. BUILD_PROFESSIONAL_INSTALLER.bat
2. Test installer
3. Sign with certificate
4. Upload to release
```

---

## 📚 ADVANCED TOPICS

### **1. Custom Splash Screen**
```python
# Add to build_installer.py
splash = Splash(
    'splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=(10, 50),
    text_color='white'
)
```

### **2. Multi-language Support**
```python
# Detect system language
import locale
lang = locale.getdefaultlocale()[0]

# Load language file
with open(f'lang/{lang}.json') as f:
    translations = json.load(f)
```

### **3. Auto-Update System**
```python
# Check for updates
def check_update():
    r = requests.get('https://api.github.com/repos/user/repo/releases/latest')
    latest = r.json()['tag_name']
    if latest > APP_VERSION:
        download_update(latest)
```

---

## 📖 DOCUMENTATION

- **README.md** - Tổng quan dự án
- **QUICKSTART.md** - Hướng dẫn nhanh
- **SMART_ANALYZER_GUIDE.md** - Smart Analyzer
- **CONVERSATION_MEMORY_ARCHITECTURE.md** - Memory system
- **MUSIC_GUIDE.md** - Music player
- **DUAL_AI_SUMMARY.txt** - Dual AI config

---

## 🔗 LINKS

- **Homepage:** https://github.com/your-repo
- **Xiaozhi Console:** https://xiaozhi.me/console
- **Documentation:** https://docs.your-site.com
- **Support:** https://discord.gg/your-server

---

## 📝 CHANGELOG

### **v4.3.0 (Current)**
- ✨ Smart Conversation Analyzer v1.0
- 🎵 VLC Music Player integration
- 💾 Conversation memory system
- 🔄 Multi-device sync (3 devices)
- 📊 141 AI tools
- 🎯 Professional installer

### **v4.2.0**
- Basic tool execution
- Xiaozhi MCP integration
- Web dashboard

---

**📅 Last Updated:** December 7, 2025  
**👤 Author:** miniZ Team  
**📦 Version:** 4.3.0 Professional Edition
