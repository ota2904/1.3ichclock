# 🚀 BUILD GUIDE - miniZ MCP v4.3.0 Professional Edition

Hướng dẫn đầy đủ để build và tạo installer chuyên nghiệp cho miniZ MCP.

---

## 📋 MỤC LỤC

1. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
2. [Cài đặt công cụ](#cài-đặt-công-cụ)
3. [Build Executable (.exe)](#build-executable-exe)
4. [Tạo Installer chuyên nghiệp](#tạo-installer-chuyên-nghiệp)
5. [Phân phối cho khách hàng](#phân-phối-cho-khách-hàng)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 YÊU CẦU HỆ THỐNG

### Minimum Requirements:
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8 hoặc cao hơn
- **RAM**: 4GB+
- **Disk Space**: 500MB cho build tools + 200MB cho output

### Dependencies:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### Optional (cho Installer):
- **Inno Setup 6.0+**: [Download tại đây](https://jrsoftware.org/isinfo.php)

---

## 🛠️ CÀI ĐẶT CÔNG CỤ

### Bước 1: Cài PyInstaller

```bash
pip install pyinstaller
```

Verify installation:
```bash
pyinstaller --version
# Output: 5.13.0 hoặc cao hơn
```

### Bước 2: Cài Inno Setup (Optional - để tạo installer)

1. Download từ: https://jrsoftware.org/isdl.php
2. Chạy file `innosetup-6.x.x.exe`
3. Follow wizard để cài đặt
4. Add vào PATH (optional):
   - `C:\Program Files (x86)\Inno Setup 6\`

---

## 🏗️ BUILD EXECUTABLE (.EXE)

### Cách 1: Sử dụng BUILD.bat (KHUYÊN DÙNG)

**Đơn giản nhất - Chỉ cần double-click!**

```bash
# Double-click vào file:
BUILD.bat

# Hoặc chạy từ command line:
.\BUILD.bat
```

Script sẽ tự động:
- ✅ Kiểm tra Python
- ✅ Cài PyInstaller (nếu chưa có)
- ✅ Cài tất cả dependencies
- ✅ Xóa build cũ
- ✅ Build file .exe
- ✅ Verify kết quả

**Output**: `dist\miniZ_MCP_v4.3.0_Professional.exe`

### Cách 2: Manual build với PyInstaller

```bash
# 1. Clean old builds
rmdir /s /q build dist

# 2. Build với spec file
pyinstaller xiaozhi_installer.spec --clean --noconfirm

# 3. Check output
dir dist\miniZ_MCP_v4.3.0_Professional.exe
```

### Kiểm tra file .exe

```bash
cd dist
.\miniZ_MCP_v4.3.0_Professional.exe
```

**Lưu ý**: Lần đầu chạy sẽ hiện cửa sổ activation license.

---

## 📦 TẠO INSTALLER CHUYÊN NGHIỆP

### Yêu cầu:
- ✅ Đã build xong file .exe (xem bước trên)
- ✅ Đã cài Inno Setup 6.0+

### Bước 1: Kiểm tra file cần thiết

Đảm bảo có đủ files sau:
```
✓ dist\miniZ_MCP_v4.3.0_Professional.exe
✓ license_manager.py
✓ activation_window.py
✓ license_generator.py
✓ LICENSE_SYSTEM_README.md
✓ README.md
✓ QUICKSTART.md
✓ LICENSE
✓ music_library\
✓ xiaozhi_endpoints.json
```

### Bước 2: Build Installer với Inno Setup

**Cách 1: GUI (Đơn giản)**

1. Mở **Inno Setup Compiler**
2. File → Open → Chọn `installer.iss`
3. Build → Compile (hoặc nhấn **Ctrl+F9**)
4. Đợi build hoàn tất (~1-2 phút)

**Cách 2: Command Line (Tự động)**

```bash
# Chạy từ PowerShell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

### Output Installer

Sau khi build xong, file installer sẽ nằm tại:

```
installer_output\miniZ_MCP_v4.3.0_Professional_Setup.exe
```

**Kích thước**: ~50-80MB (tùy dependencies)

---

## 🎁 PHÂN PHỐI CHO KHÁCH HÀNG

### Package cần giao cho khách hàng:

```
📦 miniZ_MCP_v4.3.0_Professional_Package.zip
├── 📄 miniZ_MCP_v4.3.0_Professional_Setup.exe  (Installer)
├── 📄 LICENSE_SYSTEM_README.md                  (Hướng dẫn kích hoạt)
├── 📄 QUICKSTART.md                             (Quick start guide)
└── 📄 INSTALLATION_GUIDE.txt                    (Hướng dẫn cài đặt)
```

### Tạo INSTALLATION_GUIDE.txt

```plaintext
========================================
miniZ MCP v4.3.0 PROFESSIONAL EDITION
HƯỚNG DẪN CÀI ĐẶT
========================================

BƯỚC 1: CÀI ĐẶT PHẦN MỀM
-------------------------
1. Chạy file: miniZ_MCP_v4.3.0_Professional_Setup.exe
2. Follow wizard để cài đặt
3. Chọn thư mục cài đặt (mặc định: C:\Program Files\miniZ_MCP)
4. Nhấn "Install" để bắt đầu

BƯỚC 2: KÍCH HOẠT LICENSE
--------------------------
1. Sau khi cài xong, chạy phần mềm lần đầu
2. Cửa sổ "License Activation" sẽ hiện ra
3. COPY "Hardware ID" (ví dụ: F4A9B2C1D8E5F3A7...)
4. GỬI Hardware ID cho nhà cung cấp
5. NHẬN License Key (format: XXXX-XXXX-XXXX-XXXX)
6. NHẬP License Key vào ô "License Key"
7. Nhấn "Activate"

BƯỚC 3: SỬ DỤNG
----------------
- Phần mềm sẽ tự động mở trình duyệt
- Truy cập: http://localhost:8000
- Sử dụng Web UI để điều khiển

SUPPORT:
--------
- Email: support@miniz-mcp.com
- Hotline: 1900-xxxx
- Xem thêm: LICENSE_SYSTEM_README.md

LƯU Ý:
-------
- 1 License Key = 1 máy tính
- Không chia sẻ license key
- Muốn chuyển máy → Liên hệ support
```

### Checklist giao hàng:

- [ ] Test installer trên máy sạch (clean Windows)
- [ ] Tạo 1-2 license key demo cho khách test
- [ ] Đóng gói tất cả files vào ZIP
- [ ] Upload lên cloud storage hoặc gửi qua email
- [ ] Gửi hướng dẫn kích hoạt chi tiết

---

## 🔒 QUY TRÌNH LICENSE CHO ADMIN

### Tạo License Key cho khách hàng:

```bash
# 1. Chạy License Generator
python license_generator.py

# 2. Chọn menu 1 (Tạo license mới)
1

# 3. Nhập thông tin:
Tên khách hàng: Nguyen Van A
Loại license: standard  # hoặc trial, professional, enterprise
Thời hạn (days): 365
Max devices: 1
Ghi chú: Customer ABC - Contract 2025

# 4. Key được tạo:
License Key: A2K9-7XM4-P5N8-Q3W1

# 5. Gửi key này cho khách hàng
```

### Verify activation:

```bash
python license_generator.py

# Chọn menu 3 (Kiểm tra license)
3

# Nhập key để xem trạng thái
License Key: A2K9-7XM4-P5N8-Q3W1

# Output:
Customer: Nguyen Van A
Status: active
Devices: 1/1
Expires: 2026-11-27
```

---

## 🐛 TROUBLESHOOTING

### Lỗi 1: "Python not found" khi build

**Nguyên nhân**: Python chưa được thêm vào PATH

**Giải pháp**:
```bash
# Thêm Python vào PATH:
# System Properties → Environment Variables → Path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\
C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts\
```

### Lỗi 2: "Module not found" khi chạy .exe

**Nguyên nhân**: Thiếu hidden imports trong spec file

**Giải pháp**:
1. Mở `xiaozhi_installer.spec`
2. Thêm module vào `hiddenimports`:
```python
hiddenimports = [
    'your_missing_module',
    # ... existing imports
]
```
3. Rebuild: `pyinstaller xiaozhi_installer.spec --clean`

### Lỗi 3: File .exe quá lớn (>200MB)

**Nguyên nhân**: Chứa nhiều libraries không cần thiết

**Giải pháp**:
1. Optimize spec file - Thêm vào `excludes`:
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    'scipy',
    'pytest',
    'PIL',
    'cv2',
]
```
2. Enable UPX compression:
```python
upx=True,
upx_exclude=[],
```

### Lỗi 4: VLC không phát nhạc sau khi build

**Nguyên nhân**: VLC plugins không được copy

**Giải pháp**:
1. Copy thư mục VLC vào dist:
```bash
xcopy "C:\Program Files\VideoLAN\VLC" "dist\vlc\" /E /I
```
2. Update spec file:
```python
datas = [
    ('C:/Program Files/VideoLAN/VLC', 'vlc'),
    # ... other datas
]
```

### Lỗi 5: Inno Setup không tìm thấy files

**Nguyên nhân**: Đường dẫn trong `installer.iss` sai

**Giải pháp**:
1. Kiểm tra `[Files]` section trong `installer.iss`
2. Đảm bảo paths tương đối từ thư mục project:
```ini
Source: "dist\miniZ_MCP_v4.3.0_Professional.exe"; DestDir: "{app}";
```
3. Verify files tồn tại:
```bash
dir dist\miniZ_MCP_v4.3.0_Professional.exe
```

### Lỗi 6: License activation fails sau khi install

**Nguyên nhân**: 
- Network bị chặn (nếu dùng online mode)
- Hardware ID không match

**Giải pháp**:
1. Sử dụng **Offline Mode** (check box trong activation window)
2. Verify Hardware ID:
```bash
python -c "from license_manager import get_license_manager; print(get_license_manager()._generate_hardware_id())"
```
3. Re-create license với đúng Hardware ID

### Lỗi 7: Installer bị Windows Defender block

**Nguyên nhân**: Executable chưa được signed

**Giải pháp** (Ngắn hạn):
1. Right-click file .exe → Properties
2. Check "Unblock" → Apply
3. Hoặc thêm exclusion trong Windows Defender

**Giải pháp** (Dài hạn):
1. Mua Code Signing Certificate (~$200-500/year)
2. Sign executable với SignTool:
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com miniZ_MCP_v4.3.0_Professional.exe
```

---

## 📊 FILE SIZE REFERENCE

**Typical build sizes:**

| Component | Size |
|-----------|------|
| Raw .exe (PyInstaller) | ~50-80MB |
| With VLC bundled | ~100-150MB |
| Final Installer (Inno Setup) | ~50-80MB (compressed) |
| Installed size on disk | ~150-200MB |

**Optimization tips:**
- Exclude unused libraries → Save 30-50MB
- Enable UPX compression → Save 20-30%
- Use onefile mode → Single exe (easier to distribute)

---

## 🚀 ADVANCED: AUTO-UPDATE SYSTEM

### (Optional) Thêm tính năng auto-update

**File structure:**
```
version_info.json (host trên server)
{
    "version": "4.3.1",
    "download_url": "https://yoursite.com/miniZ_MCP_v4.3.1_Setup.exe",
    "release_notes": "Bug fixes and improvements"
}
```

**Code mẫu** (thêm vào xiaozhi_final.py):
```python
import requests

def check_for_updates():
    try:
        resp = requests.get("https://yoursite.com/version_info.json")
        data = resp.json()
        current_version = "4.3.0"
        if data['version'] > current_version:
            print(f"New version available: {data['version']}")
            print(f"Download: {data['download_url']}")
    except:
        pass
```

---

## 📞 SUPPORT

Nếu gặp vấn đề khi build:
1. Check log files: `build/*/warn-*.txt`
2. Re-run với `--debug` flag:
   ```bash
   pyinstaller xiaozhi_installer.spec --debug=all
   ```
3. Search error trên PyInstaller Issues: https://github.com/pyinstaller/pyinstaller/issues

---

## ✅ CHECKLIST TRƯỚC KHI PHÁT HÀNH

### Pre-release Checklist:

- [ ] Test executable trên Windows 10
- [ ] Test executable trên Windows 11
- [ ] Test installer (install + uninstall)
- [ ] Test license activation flow
- [ ] Test license deactivation/transfer
- [ ] Test offline activation mode
- [ ] Verify all features work (Music, AI, VLC)
- [ ] Check file size (<100MB preferred)
- [ ] Create demo license keys
- [ ] Prepare customer documentation
- [ ] Upload to distribution channel
- [ ] Test download link
- [ ] Send to beta testers
- [ ] Collect feedback
- [ ] Fix critical bugs
- [ ] Final release! 🎉

---

**Chúc bạn build thành công! 🚀**

*Last updated: November 27, 2025*
