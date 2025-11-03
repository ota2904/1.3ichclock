"""
Build script for Xiaozhi MCP Control Panel Installer
Tạo file .exe standalone với PyInstaller
"""

import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """Kiểm tra PyInstaller đã cài chưa"""
    try:
        import PyInstaller
        print("✅ PyInstaller đã cài đặt")
        return True
    except ImportError:
        print("❌ PyInstaller chưa cài đặt")
        print("📦 Đang cài đặt PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ Đã cài đặt PyInstaller")
        return True

def clean_build_folders():
    """Xóa các folder build cũ"""
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            print(f"🗑️  Xóa folder {folder}/")
            shutil.rmtree(folder)
    
    # Xóa file .spec cũ
    spec_file = "xiaozhi_installer.spec"
    if os.path.exists(spec_file):
        print(f"🗑️  Xóa file {spec_file}")
        os.remove(spec_file)

def create_spec_file():
    """Tạo file .spec cho PyInstaller"""
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['xiaozhi_final.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('requirements.txt', '.'),
        ('README.md', '.'),
        ('QUICKSTART.md', '.'),
        ('CHANGELOG.md', '.'),
        ('MUSIC_GUIDE.md', '.'),
        ('MUSIC_LIBRARY.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'fastapi',
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'websockets',
        'websockets.legacy',
        'websockets.legacy.server',
        'beautifulsoup4',
        'bs4',
        'requests',
        'feedparser',
        'pyautogui',
        'PIL',
        'psutil',
        'pycaw',
        'comtypes',
        'win32api',
        'win32con',
        'win32gui',
        'win32com',
        'win32com.client',
        'pythoncom',
        'pywintypes',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tensorflow',
        'torch',
        'jupyter',
        'notebook',
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
    name='XiaozhiMCP_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Hiển thị console để xem log
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Có thể thêm icon .ico nếu muốn
)
"""
    
    with open("xiaozhi_installer.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✅ Đã tạo file xiaozhi_installer.spec")

def build_executable():
    """Build file .exe với PyInstaller"""
    print("\n" + "="*60)
    print("🚀 BẮT ĐẦU BUILD EXECUTABLE")
    print("="*60 + "\n")
    
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--clean",
        "--noconfirm",
        "xiaozhi_installer.spec"
    ]
    
    print(f"📦 Command: {' '.join(cmd)}")
    print("\n⏳ Đang build... (có thể mất vài phút)\n")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*60)
        print("✅ BUILD THÀNH CÔNG!")
        print("="*60)
        return True
    except subprocess.CalledProcessError as e:
        print("\n" + "="*60)
        print("❌ BUILD THẤT BẠI!")
        print("="*60)
        print(f"Error: {e}")
        return False

def create_release_folder():
    """Tạo folder release với tất cả file cần thiết"""
    release_folder = "Xiaozhi_MCP_Release"
    
    if os.path.exists(release_folder):
        print(f"🗑️  Xóa folder {release_folder}/ cũ")
        shutil.rmtree(release_folder)
    
    os.makedirs(release_folder)
    print(f"📁 Tạo folder {release_folder}/")
    
    # Copy file .exe
    exe_file = "dist/XiaozhiMCP_Installer.exe"
    if os.path.exists(exe_file):
        shutil.copy2(exe_file, f"{release_folder}/XiaozhiMCP.exe")
        print(f"✅ Copy XiaozhiMCP.exe")
    
    # Copy các file hướng dẫn
    docs = [
        'README.md',
        'QUICKSTART.md',
        'CHANGELOG.md',
        'MUSIC_GUIDE.md',
        'MUSIC_LIBRARY.md',
        'LICENSE',
        'requirements.txt'
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, f"{release_folder}/{doc}")
            print(f"✅ Copy {doc}")
    
    # Copy batch files
    batch_files = [
        'INSTALL.bat',
        'START.bat',
        'CHECK.bat',
        'CREATE_SHORTCUT.bat'
    ]
    
    for bat in batch_files:
        if os.path.exists(bat):
            shutil.copy2(bat, f"{release_folder}/{bat}")
            print(f"✅ Copy {bat}")
    
    # Tạo folder music_library
    os.makedirs(f"{release_folder}/music_library", exist_ok=True)
    print(f"✅ Tạo folder music_library/")
    
    # Tạo file SETUP_GUIDE.txt
    setup_guide = f"""
╔══════════════════════════════════════════════════════════════╗
║           XIAOZHI MCP CONTROL PANEL - HƯỚNG DẪN CÀI ĐẶT      ║
╚══════════════════════════════════════════════════════════════╝

🎯 PHIÊN BẢN: v4.0.0 - Production Release
📅 BUILD DATE: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 NỘI DUNG PACKAGE:

├── XiaozhiMCP.exe              → File chương trình chính (Standalone)
├── INSTALL.bat                 → Script cài đặt Python dependencies
├── START.bat                   → Script khởi động nhanh
├── CHECK.bat                   → Kiểm tra cài đặt
├── CREATE_SHORTCUT.bat         → Tạo shortcut desktop
├── README.md                   → Tài liệu chính
├── QUICKSTART.md               → Hướng dẫn nhanh
├── MUSIC_GUIDE.md              → Hướng dẫn thư viện nhạc
├── CHANGELOG.md                → Lịch sử phiên bản
├── LICENSE                     → Giấy phép MIT
├── requirements.txt            → Danh sách dependencies
└── music_library/              → Thư mục nhạc (thêm file .mp3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ CÁCH 1: CHẠY FILE .EXE (KHUYẾN NGHỊ)

1️⃣ Nhấp đúp vào: XiaozhiMCP.exe
2️⃣ Server tự động khởi động tại: http://localhost:8000
3️⃣ Trình duyệt tự động mở Dashboard
4️⃣ Cấu hình token qua icon ⚙️

✅ KHÔNG CẦN CÀI PYTHON hay DEPENDENCIES!
✅ FILE .EXE ĐÃ CHỨA TẤT CẢ THƯ VIỆN CẦN THIẾT!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐍 CÁCH 2: CHẠY TỪ SOURCE CODE (Advanced)

Yêu cầu: Python 3.8+

1️⃣ Cài đặt dependencies:
   → Nhấp đúp INSTALL.bat
   HOẶC: pip install -r requirements.txt

2️⃣ Khởi động server:
   → Nhấp đúp START.bat
   HOẶC: python xiaozhi_final.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 LẤY XIAOZHI TOKEN:

1. Truy cập: https://xiaozhi.me
2. Đăng nhập (Google/Email)
3. Profile → MCP Settings
4. Copy JWT token

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ TÍNH NĂNG CHÍNH:

✅ 35+ công cụ điều khiển máy tính
✅ Thư viện nhạc tự động (music_library/)
✅ Giá vàng real-time (GiaVang.org)
✅ Tin tức VnExpress theo chủ đề
✅ YouTube controls & Website access
✅ Dashboard UI hiện đại
✅ Multi-device endpoint support

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 QUICK TIPS:

📌 Tạo shortcut desktop:
   → Chạy CREATE_SHORTCUT.bat

📌 Kiểm tra cài đặt:
   → Chạy CHECK.bat

📌 Thêm nhạc:
   → Copy file .mp3 vào music_library/

📌 Xem log:
   → Dashboard → Tab "📋 Log"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📞 HỖ TRỢ:

🌐 GitHub: https://github.com/nguyenconghuy2904-source/miniz_pc_toolfix
📖 Docs: Xem README.md và QUICKSTART.md
🐛 Issues: GitHub Issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 LICENSE: MIT License
❤️  Made with love for Xiaozhi MCP

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    with open(f"{release_folder}/SETUP_GUIDE.txt", "w", encoding="utf-8") as f:
        f.write(setup_guide)
    
    print(f"✅ Tạo SETUP_GUIDE.txt")
    
    print("\n" + "="*60)
    print(f"✅ HOÀN TẤT! Package nằm trong folder: {release_folder}/")
    print("="*60)
    
    # Hiển thị thông tin file size
    exe_path = f"{release_folder}/XiaozhiMCP.exe"
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n📦 Kích thước file .exe: {size_mb:.2f} MB")

def main():
    """Main build process"""
    print("\n" + "="*60)
    print("🏗️  XIAOZHI MCP INSTALLER BUILDER")
    print("="*60 + "\n")
    
    # Kiểm tra PyInstaller
    if not check_pyinstaller():
        print("❌ Không thể cài PyInstaller!")
        return False
    
    print()
    
    # Xóa build cũ
    clean_build_folders()
    print()
    
    # Tạo file .spec
    create_spec_file()
    print()
    
    # Build executable
    if not build_executable():
        return False
    
    print()
    
    # Tạo release folder
    create_release_folder()
    
    print("\n" + "="*60)
    print("🎉 BUILD HOÀN TẤT!")
    print("="*60)
    print("\n📂 File .exe có tại: Xiaozhi_MCP_Release/XiaozhiMCP.exe")
    print("📖 Xem hướng dẫn: Xiaozhi_MCP_Release/SETUP_GUIDE.txt")
    print("\n💡 TIPS:")
    print("   - Chạy XiaozhiMCP.exe để khởi động server")
    print("   - Không cần cài Python hay dependencies")
    print("   - File .exe là standalone, có thể copy sang máy khác")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ SUCCESS!\n")
            sys.exit(0)
        else:
            print("\n❌ FAILED!\n")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Build bị hủy bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
