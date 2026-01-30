# miniZ MCP v4.3.0 - HƯỚNG DẪN TẠO INSTALLER EXE

## 📦 TỔNG QUAN

Hệ thống installer này tạo file `.exe` với đầy đủ bảo mật:
- ✅ License key validation
- ✅ Hardware ID binding (gắn với máy tính cụ thể)
- ✅ GUI installer với tkinter
- ✅ Copy files và cài đặt tự động
- ✅ Điều khoản sử dụng và bảo mật

## 🚀 CÁCH SỬ DỤNG

### Bước 1: Build Installer EXE

```bash
# Chạy script build
BUILD_INSTALLER.bat
```

Script sẽ:
1. Cài đặt PyInstaller (nếu chưa có)
2. Build file EXE từ `installer_setup.py`
3. Tạo file `miniZ_MCP_Installer_v4.3.0.exe` trong thư mục `dist/`

### Bước 2: Tạo License Key cho Khách Hàng

#### 2.1. Lấy Hardware ID từ khách hàng

Khách hàng chạy installer và copy Hardware ID hiển thị:

```
Hardware ID: 1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P
```

#### 2.2. Generate License Key

Chạy tool generate license:

```bash
python installer_setup.py generate
```

Nhập thông tin:
```
Enter Hardware ID: 1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P
Customer Name [User]: Nguyen Van A
License Type (standard/pro/enterprise) [standard]: pro
Valid Days [365]: 365
```

Kết quả:
```
✅ License Key Generated Successfully!
================================================================
License Key: 1A2B-3C4D-5E6F-7G8H-9I0J

Customer: Nguyen Van A
Type: pro
Expiry: 20251206
Hardware ID: 1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P
================================================================
```

License được lưu vào file `license_info.txt`

### Bước 3: Gửi License cho Khách Hàng

Gửi cho khách hàng:
- 📧 License Key: `1A2B-3C4D-5E6F-7G8H-9I0J`
- 📄 File `license_info.txt` (optional)

### Bước 4: Khách Hàng Cài Đặt

1. Chạy `miniZ_MCP_Installer_v4.3.0.exe`
2. Copy Hardware ID (nếu chưa gửi)
3. Nhập License Key nhận được
4. Click "✅ Kiểm tra License"
5. Chọn thư mục cài đặt
6. Đồng ý điều khoản
7. Click "🚀 Cài đặt miniZ MCP"

## 🔐 BẢO MẬT

### Hardware ID Binding

License key được gắn với Hardware ID duy nhất:
- ✅ Dựa trên MAC address, CPU ID, Computer name
- ✅ Không thể dùng trên máy khác
- ✅ Hash SHA-256 bảo mật

### License Key Format

```
Format: XXXX-XXXX-XXXX-XXXX-XXXX (20 ký tự)

Cấu trúc:
- 8 ký tự đầu: Hardware ID hash
- 12 ký tự sau: Signature hash (customer + type + expiry)
```

### Validation Process

```python
1. Extract hardware ID từ license key (8 ký tự đầu)
2. So sánh với hardware ID của máy hiện tại
3. Nếu khớp → License hợp lệ ✅
4. Nếu không khớp → License không hợp lệ ❌
```

## 🎨 INSTALLER GUI

### Giao Diện

```
┌─────────────────────────────────────────┐
│   🚀 miniZ MCP                          │
│   Professional Edition v4.3.0           │
├─────────────────────────────────────────┤
│                                         │
│  🔑 Hardware ID                         │
│  ┌───────────────────────────────────┐  │
│  │ 1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P │  │
│  └───────────────────────────────────┘  │
│  [📋 Copy Hardware ID]                  │
│                                         │
│  🔐 License Key                         │
│  ┌───────────────────────────────────┐  │
│  │ XXXX-XXXX-XXXX-XXXX-XXXX          │  │
│  └───────────────────────────────────┘  │
│  [✅ Kiểm tra License]                  │
│                                         │
│  📁 Thư mục cài đặt                     │
│  ┌─────────────────────┬─────────────┐  │
│  │ C:\Users\...\miniZ  │ [📂 Browse] │  │
│  └─────────────────────┴─────────────┘  │
│                                         │
│  ☑ Tôi đồng ý với điều khoản...         │
│                                         │
│  [🚀 Cài đặt miniZ MCP]                 │
│                                         │
└─────────────────────────────────────────┘
```

## 📋 FILES

```
BUILD_INSTALLER.bat         - Script build EXE
installer_setup.py          - Main installer code
installer.spec              - PyInstaller config
version_info.txt            - Windows version info
build_config.toml           - Build configuration

dist/
  miniZ_MCP_Installer_v4.3.0.exe  - File installer final
```

## 🛠️ TOOLS

### 1. Lấy Hardware ID của máy hiện tại

```bash
python installer_setup.py hwid
```

Output:
```
🔑 Hardware ID: 1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P
```

### 2. Generate License Key

```bash
python installer_setup.py generate
```

### 3. Test Installer GUI

```bash
python installer_setup.py
```

## 🎯 LICENSE TYPES

### Standard License
- ✅ Sử dụng cá nhân
- ✅ 1 máy tính
- ✅ Cập nhật 1 năm
- ⚠️ Không thương mại

### Pro License
- ✅ Sử dụng chuyên nghiệp
- ✅ 1 máy tính
- ✅ Cập nhật 1 năm
- ✅ Hỗ trợ ưu tiên

### Enterprise License
- ✅ Sử dụng doanh nghiệp
- ✅ Nhiều máy tính
- ✅ Cập nhật không giới hạn
- ✅ Hỗ trợ 24/7

## 🔧 TROUBLESHOOTING

### Build Error: PyInstaller not found

```bash
pip install pyinstaller
```

### Build Error: Module not found

Thêm vào `installer.spec`:
```python
hiddenimports=[
    'your_module_name',
]
```

### License Key Invalid

- ✅ Kiểm tra Hardware ID có đúng không
- ✅ Kiểm tra format: XXXX-XXXX-XXXX-XXXX-XXXX
- ✅ Kiểm tra license có hết hạn không

### Installer Crash

- Chạy từ CMD để xem error: `miniZ_MCP_Installer_v4.3.0.exe`
- Check Windows Event Viewer

## 📊 STATISTICS

### Build Size
- Installer EXE: ~15-20 MB (tùy dependencies)
- Installed size: ~50-100 MB

### Performance
- Build time: 1-2 phút
- Install time: 30-60 giây

## 🔄 UPDATE PROCESS

Khi có phiên bản mới:

1. Cập nhật `version` trong `installer_setup.py`
2. Cập nhật `version_info.txt`
3. Build lại EXE: `BUILD_INSTALLER.bat`
4. Generate license mới cho khách hàng (nếu cần)

## 📞 SUPPORT

Nếu khách hàng gặp vấn đề:
1. Yêu cầu gửi Hardware ID
2. Kiểm tra license key có đúng không
3. Generate license mới nếu cần
4. Hướng dẫn cài đặt lại

## ⚡ QUICK REFERENCE

```bash
# Build installer
BUILD_INSTALLER.bat

# Get hardware ID
python installer_setup.py hwid

# Generate license
python installer_setup.py generate

# Test installer GUI
python installer_setup.py
```

---

© 2024-2025 miniZ MCP. All rights reserved.
