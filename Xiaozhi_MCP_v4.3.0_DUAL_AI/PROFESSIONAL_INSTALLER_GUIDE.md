# miniZ MCP v4.3.0 - PROFESSIONAL INSTALLER GUIDE
# Hướng dẫn tạo installer chuyên nghiệp với 150 license keys sẵn

## 🎯 TỔNG QUAN

Hệ thống installer chuyên nghiệp bao gồm:

✅ **150 License Keys sẵn** (100 Standard + 40 Pro + 10 Enterprise)
✅ **Inno Setup Installer** - Chuẩn Windows với Next/Next/Finish
✅ **EULA đầy đủ** - Điều khoản, miễn trừ trách nhiệm về dữ liệu
✅ **Icon & Branding** - Professional UI
✅ **Auto Installation** - Tự động cài dependencies
✅ **Shortcuts** - Desktop, Start Menu, Quick Launch
✅ **Uninstaller** - Gỡ cài đặt sạch sẽ

---

## 📦 CÁC FILE ĐÃ TẠO

```
generate_license_batch.py          → Tạo 150 license keys
setup_inno.iss                      → Inno Setup script
LICENSE_AGREEMENT.txt               → EULA đầy đủ điều khoản
README_INSTALL.txt                  → Thông tin trước cài đặt
POST_INSTALL_INFO.txt               → Hướng dẫn sau cài đặt
BUILD_PROFESSIONAL_INSTALLER.bat    → Script build tự động
```

---

## 🚀 CÁCH BUILD INSTALLER

### Bước 1: Cài đặt Inno Setup

```
1. Download Inno Setup 6:
   → https://jrsoftware.org/isdl.php

2. Chạy installer và cài đặt vào thư mục mặc định:
   → C:\Program Files (x86)\Inno Setup 6\

3. Hoàn tất cài đặt
```

### Bước 2: Generate License Keys

```bash
# Chạy script tạo 150 keys
python generate_license_batch.py
```

**Output:**
- `LICENSE_KEYS.txt` - Danh sách 150 keys dễ đọc
- `licenses_all.json` - Tất cả keys (JSON)
- `licenses_standard.json` - 100 Standard keys
- `licenses_pro.json` - 40 Pro keys
- `licenses_enterprise.json` - 10 Enterprise keys
- `license_tracking.json` - File theo dõi usage

### Bước 3: Build Installer

```bash
# Chạy script build
BUILD_PROFESSIONAL_INSTALLER.bat
```

**Quy trình:**
1. ✅ Kiểm tra/tạo license keys
2. ✅ Kiểm tra Inno Setup
3. ✅ Chuẩn bị files
4. ✅ Compile installer
5. ✅ Tạo file `.exe` trong `installer_output/`

**Output:**
```
installer_output/
  └── miniZ_MCP_Setup_v4.3.0.exe  (~30-50 MB)
```

---

## 🔑 150 LICENSE KEYS

### Phân loại

| Type | Số lượng | Thời hạn | Mục đích |
|------|----------|----------|----------|
| **Standard** | 100 keys | 365 ngày | Cá nhân, phi thương mại |
| **Pro** | 40 keys | 730 ngày | Chuyên nghiệp |
| **Enterprise** | 10 keys | 1825 ngày | Doanh nghiệp, nhiều máy |

### Format

```
XXXX-XXXX-XXXX-XXXX-XXXX

Ví dụ:
- Standard:   A3F9-K2L4-M8N1-P5Q7-R9S2
- Pro:        B4G8-L3M5-N9P2-Q6R8-S1T4
- Enterprise: C5H9-M4N6-P1Q3-R7S9-T2U5
```

### Xem danh sách keys

```bash
# Xem trong file text
notepad LICENSE_KEYS.txt

# Hoặc xem JSON
notepad licenses_all.json
```

---

## 📋 EULA - ĐIỀU KHOẢN QUAN TRỌNG

### Giới hạn trách nhiệm

✅ **Đã bao gồm trong `LICENSE_AGREEMENT.txt`:**

```
⚠️ CHÚNG TÔI KHÔNG CHỊU TRÁCH NHIỆM VỀ:
  ✗ Mất mát, hư hỏng, hoặc xóa dữ liệu của bạn
  ✗ Thiệt hại gián tiếp, ngẫu nhiên, đặc biệt
  ✗ Kết quả không chính xác từ AI
  ✗ Chi phí API từ bên thứ ba
  ✗ Bất kỳ thiệt hại nào phát sinh

NGƯỜI DÙNG CHỊU TRÁCH NHIỆM:
  ✓ Sao lưu dữ liệu TRƯỚC KHI sử dụng
  ✓ Kiểm tra kết quả AI trước khi áp dụng
  ✓ Bảo mật License Key và API Keys
  ✓ Sử dụng hợp pháp và có đạo đức
```

### Quyền lợi người dùng

```
✓ Cài đặt theo số máy của license
✓ Nhận cập nhật trong thời hạn
✓ Hỗ trợ kỹ thuật theo loại license
✓ Gia hạn khi hết hạn
```

### Hạn chế

```
✗ Không chia sẻ License Key
✗ Không reverse engineer
✗ Không sử dụng vượt license
✗ Không dùng cho mục đích bất hợp pháp
```

---

## 🎨 INSTALLER UI FLOW

### Màn hình 1: Welcome
```
┌─────────────────────────────────────────┐
│  Chào mừng đến với miniZ MCP v4.3.0     │
│                                         │
│  Professional AI & Voice Control        │
│                                         │
│  [Next]  [Cancel]                       │
└─────────────────────────────────────────┘
```

### Màn hình 2: License Agreement (EULA)
```
┌─────────────────────────────────────────┐
│  END USER LICENSE AGREEMENT             │
│  ┌───────────────────────────────────┐  │
│  │ ⚠️ Đọc kỹ điều khoản...           │  │
│  │ • Quyền và trách nhiệm            │  │
│  │ • Giới hạn trách nhiệm về dữ liệu │  │
│  │ • Không bảo đảm                   │  │
│  └───────────────────────────────────┘  │
│  ☑ I accept the agreement               │
│  [Next]  [Cancel]                       │
└─────────────────────────────────────────┘
```

### Màn hình 3: License Key Input
```
┌─────────────────────────────────────────┐
│  License Key Activation                 │
│                                         │
│  Nhập License Key:                      │
│  ┌───────────────────────────────────┐  │
│  │ XXXX-XXXX-XXXX-XXXX-XXXX          │  │
│  └───────────────────────────────────┘  │
│                                         │
│  Format: XXXX-XXXX-XXXX-XXXX-XXXX      │
│                                         │
│  [Next]  [Back]  [Cancel]               │
└─────────────────────────────────────────┘
```

### Màn hình 4: Install Location
```
┌─────────────────────────────────────────┐
│  Chọn thư mục cài đặt                   │
│                                         │
│  ┌─────────────────────────┬─────────┐  │
│  │ C:\Program Files\miniZ  │ Browse  │  │
│  └─────────────────────────┴─────────┘  │
│                                         │
│  Space required: 100 MB                 │
│  Space available: 50 GB                 │
│                                         │
│  [Next]  [Back]  [Cancel]               │
└─────────────────────────────────────────┘
```

### Màn hình 5: Select Tasks
```
┌─────────────────────────────────────────┐
│  Additional Tasks                       │
│                                         │
│  Shortcuts:                             │
│  ☑ Tạo Desktop shortcut                 │
│  ☐ Tạo Quick Launch icon                │
│  ☑ Thêm vào Start Menu                  │
│                                         │
│  [Next]  [Back]  [Cancel]               │
└─────────────────────────────────────────┘
```

### Màn hình 6: Ready to Install
```
┌─────────────────────────────────────────┐
│  Sẵn sàng cài đặt                       │
│                                         │
│  Destination: C:\Program Files\miniZ    │
│  License: Pro (valid 730 days)          │
│  Tasks: Desktop shortcut, Start Menu    │
│                                         │
│  [Install]  [Back]  [Cancel]            │
└─────────────────────────────────────────┘
```

### Màn hình 7: Installing
```
┌─────────────────────────────────────────┐
│  Đang cài đặt...                        │
│                                         │
│  [████████████████░░░░░░░░░░] 75%       │
│                                         │
│  Đang cài đặt Python dependencies...    │
│                                         │
│  [Cancel]                               │
└─────────────────────────────────────────┘
```

### Màn hình 8: Finish
```
┌─────────────────────────────────────────┐
│  ✅ Cài đặt hoàn tất!                   │
│                                         │
│  miniZ MCP v4.3.0 đã sẵn sàng           │
│                                         │
│  ☑ Xem hướng dẫn sau cài đặt            │
│  ☑ Khởi động miniZ MCP                  │
│                                         │
│  [Finish]                               │
└─────────────────────────────────────────┘
```

---

## 📤 PHÂN PHỐI CHO KHÁCH HÀNG

### Bước 1: Chuẩn bị

```
✓ File installer: miniZ_MCP_Setup_v4.3.0.exe
✓ Chọn license key từ LICENSE_KEYS.txt
✓ Lưu thông tin khách hàng
```

### Bước 2: Gửi cho khách hàng

**Email template:**

```
Subject: miniZ MCP v4.3.0 - Installation Package

Kính gửi [Tên khách hàng],

Cảm ơn bạn đã mua miniZ MCP v4.3.0!

📦 INSTALLER:
   - File đính kèm: miniZ_MCP_Setup_v4.3.0.exe
   - Size: ~40 MB

🔑 LICENSE KEY:
   - Key của bạn: XXXX-XXXX-XXXX-XXXX-XXXX
   - Loại: [Standard/Pro/Enterprise]
   - Thời hạn: [365/730/1825] ngày
   
📋 HƯỚNG DẪN CÀI ĐẶT:
   1. Download file .exe đính kèm
   2. Double-click để chạy installer
   3. Đọc và chấp nhận điều khoản EULA
   4. Nhập license key ở trên
   5. Chọn thư mục cài đặt
   6. Click Next/Next/Finish
   7. Cấu hình API keys (xem hướng dẫn trong app)
   8. Khởi động từ Desktop shortcut

⚠️ LƯU Ý:
   - Đọc kỹ EULA về giới hạn trách nhiệm
   - Sao lưu dữ liệu trước khi sử dụng
   - Không chia sẻ license key

📞 HỖ TRỢ:
   Email: support@miniZ-mcp.com
   
Chúc bạn sử dụng hiệu quả!

Best regards,
miniZ MCP Team
```

### Bước 3: Theo dõi license

```bash
# Mở file tracking
notepad license_tracking.json

# Đánh dấu key đã sử dụng
{
  "key_id": 15,
  "license_key": "A3F9-K2L4-M8N1-P5Q7-R9S2",
  "status": "used",  ← Đổi từ "available" → "used"
  "customer_name": "Nguyen Van A",
  "customer_email": "email@example.com",
  "activated_date": "2025-12-06"
}
```

---

## 🎯 KHÁCH HÀNG SỬ DỤNG

### Cài đặt (5 phút)

1. **Download** file .exe
2. **Double-click** để chạy
3. **Chấp nhận** EULA
4. **Nhập** license key
5. **Chọn** thư mục
6. **Click** Install
7. **Đợi** cài đặt xong
8. **Finish**

### Cấu hình (2 phút)

1. **Mở** `xiaozhi_endpoints.json`
2. **Nhập** API keys:
   ```json
   {
     "gemini_api_key": "YOUR_KEY",
     "openai_api_key": "YOUR_KEY"
   }
   ```
3. **Save** file

### Khởi động

1. **Double-click** Desktop shortcut "miniZ MCP"
2. **Mở browser**: `http://localhost:8000`
3. **Bắt đầu** sử dụng!

---

## 🔧 TROUBLESHOOTING

### Build Errors

**❌ Lỗi: "Inno Setup not found"**
```
Solution: Cài đặt Inno Setup 6 từ jrsoftware.org
```

**❌ Lỗi: "File not found"**
```
Solution: Kiểm tra tất cả files trong setup_inno.iss có tồn tại
```

**❌ Lỗi: "Compilation failed"**
```
Solution: Mở setup_inno.iss bằng Inno Setup IDE để xem lỗi chi tiết
```

### Installation Errors

**❌ Lỗi: "Invalid license key"**
```
Solution: Kiểm tra format XXXX-XXXX-XXXX-XXXX-XXXX
```

**❌ Lỗi: "Python not found"**
```
Solution: Cài đặt Python 3.8+ từ python.org
```

**❌ Lỗi: "Port 8000 in use"**
```
Solution: Tắt app đang dùng port 8000
```

---

## 📊 STATISTICS

### Installer Size
- Base installer: ~15-20 MB
- With dependencies: ~40-50 MB
- Installed size: ~100-150 MB

### Build Time
- Generate keys: 5 seconds
- Compile installer: 30-60 seconds
- Total: ~1-2 minutes

### Install Time
- Copy files: 10 seconds
- Install dependencies: 2-3 minutes
- Total: ~3-5 minutes

---

## 🔄 UPDATE WORKFLOW

Khi có version mới:

```bash
1. Update version trong setup_inno.iss:
   #define MyAppVersion "4.4.0"

2. Update CHANGELOG.md với changes

3. Rebuild installer:
   BUILD_PROFESSIONAL_INSTALLER.bat

4. Test installation trên máy sạch

5. Distribute new installer
```

---

## 🎁 BONUS: Auto-Update System

Thêm auto-update checker trong code:

```python
# Thêm vào xiaozhi_final.py
def check_for_updates():
    current_version = "4.3.0"
    update_url = "https://api.github.com/repos/miniz-mcp/releases/latest"
    
    try:
        response = requests.get(update_url)
        latest = response.json()["tag_name"]
        
        if latest > current_version:
            return {
                "update_available": True,
                "latest_version": latest,
                "download_url": latest["assets"][0]["browser_download_url"]
            }
    except:
        pass
    
    return {"update_available": False}
```

---

## ✅ CHECKLIST BEFORE RELEASE

```
PRE-BUILD:
☐ All source files present
☐ API documentation complete
☐ README files updated
☐ CHANGELOG current
☐ License terms reviewed

BUILD:
☐ 150 keys generated
☐ Inno Setup installed
☐ Installer compiled successfully
☐ Output .exe created

TEST:
☐ Install on clean Windows 10
☐ Install on clean Windows 11
☐ Test license validation
☐ Test all features work
☐ Test uninstaller
☐ Check shortcuts work

DISTRIBUTION:
☐ Final installer tested
☐ Keys allocated to customers
☐ Tracking system ready
☐ Support email ready
☐ Documentation available
```

---

## 📞 SUPPORT

Cần giúp đỡ?

**Build Issues:**
- Check Inno Setup documentation
- Review .iss file syntax
- Test file paths

**License Issues:**
- Verify key format
- Check tracking JSON
- Review customer info

**Distribution:**
- Test installer on clean machine
- Verify all dependencies
- Check shortcuts and icons

---

© 2024-2025 miniZ MCP Team. All rights reserved.

**Version:** 4.3.0  
**Last Updated:** December 6, 2025  
**Build System:** Inno Setup 6.x
