# 🔐 HƯỚNG DẪN KÍCH HOẠT LICENSE - miniZ MCP Professional

## 📋 THÔNG TIN HỆ THỐNG LICENSE

### **150 License Keys Vĩnh Viễn**
- **100 STANDARD Keys** - 1 thiết bị
- **40 PRO Keys** - 2 thiết bị  
- **10 ENTERPRISE Keys** - 5 thiết bị

### **Bảo Mật Cao**
✅ **Hardware-Locked**: License gắn với CPU + Motherboard  
✅ **Mã hóa AES-256**: File license được encrypt  
✅ **Không thể copy**: Không hoạt động trên máy khác  
✅ **Lifetime**: Không hết hạn  

---

## 🚀 CÁCH KÍCH HOẠT

### **Bước 1: Nhận License Key**
Nhận 1 trong 150 keys từ nhà phân phối:
```
Ví dụ: MINIZ-STD5-G3YE-7L5J-57ND
```

### **Bước 2: Kích Hoạt Lần Đầu**

#### **Option A: Qua Web Dashboard**
1. Mở miniZ MCP Dashboard: `http://localhost:8000`
2. Click **Settings** → **License**
3. Nhập License Key
4. Click **Activate**
5. ✅ Done!

#### **Option B: Qua Command Line**
```bash
python
>>> from license_system import LicenseManager
>>> manager = LicenseManager()
>>> result = manager.activate_license("MINIZ-STD5-G3YE-7L5J-57ND")
>>> print(result["message"])
```

### **Bước 3: Xác Minh**
Sau khi kích hoạt, mỗi lần khởi động app sẽ tự động validate license.

---

## 🔍 KIỂM TRA TRẠNG THÁI LICENSE

### **Xem Thông Tin License**
```python
from license_system import LicenseManager

manager = LicenseManager()
info = manager.get_license_info()

print(f"✅ Valid: {info['valid']}")
print(f"📦 Tier: {info['tier']}")
print(f"🔑 Key: {info['license_key']}")
print(f"💻 Hardware ID: {info['hardware_id']}")
print(f"📅 Activated: {info['activated_at']}")
```

### **Qua Web API**
```bash
GET http://localhost:8000/api/license/info
```

---

## 📦 PHÂN PHỐI CHO KHÁCH HÀNG

### **File Cần Gửi**
1. ✅ **miniZ_MCP_Professional_Setup_v4.3.0.exe** - Installer
2. ✅ **1 License Key** (từ danh sách 150 keys)
3. ✅ **LICENSE_ACTIVATION_GUIDE.md** (file này)

### **Hướng Dẫn Khách Hàng**
1. Cài đặt từ file `.exe`
2. Khởi động app → hiện form **"Enter License"**
3. Nhập key đã nhận
4. Click **Activate**
5. App sẽ tự động gắn với máy tính

---

## 🔧 QUẢN LÝ LICENSE

### **Danh Sách 150 Keys**
File: `LICENSE_KEYS.json`
```json
{
  "STANDARD": [100 keys...],
  "PRO": [40 keys...],
  "ENTERPRISE": [10 keys...]
}
```

### **Tracking Keys Đã Sử Dụng**
Tạo file `LICENSE_TRACKING.json`:
```json
{
  "MINIZ-STD5-G3YE-7L5J-57ND": {
    "tier": "STANDARD",
    "status": "ACTIVATED",
    "customer_name": "Nguyễn Văn A",
    "customer_email": "nguyenvana@email.com",
    "hardware_id": "E7AC0786668E0FF0F02B62BD04F45FF6",
    "activated_at": "2025-12-08",
    "devices_used": 1,
    "devices_allowed": 1
  }
}
```

### **Thu Hồi License** (Nếu cần)
Xóa key khỏi `LICENSE_KEYS.json` → key sẽ không còn valid.

---

## 🛠️ XỬ LÝ SỰ CỐ

### **Vấn Đề 1: "License key format không hợp lệ"**
- **Nguyên nhân**: Key bị gõ sai
- **Giải pháp**: Kiểm tra lại format `MINIZ-XXXX-XXXX-XXXX-XXXX`

### **Vấn Đề 2: "License không tồn tại"**
- **Nguyên nhân**: Key không có trong database
- **Giải pháp**: Kiểm tra file `LICENSE_KEYS.json`

### **Vấn Đề 3: "License không khớp với máy này"**
- **Nguyên nhân**: Copy license file từ máy khác
- **Giải pháp**: Phải kích hoạt lại trên máy mới

### **Vấn Đề 4: Khách hàng đổi máy**
- **Giải pháp**:
  1. Deactivate license trên máy cũ
  2. Activate lại trên máy mới
  3. Hoặc cấp key mới (nếu đã hết devices allowed)

---

## 📊 THỐNG KÊ LICENSE

### **Script Kiểm Tra Keys Còn Lại**
```python
import json

# Load keys database
with open('LICENSE_KEYS.json', 'r') as f:
    all_keys = json.load(f)

# Load tracking (keys đã dùng)
try:
    with open('LICENSE_TRACKING.json', 'r') as f:
        tracking = json.load(f)
except:
    tracking = {}

# Tính toán
for tier, keys in all_keys.items():
    total = len(keys)
    used = sum(1 for k in keys if k in tracking)
    available = total - used
    
    print(f"{tier}:")
    print(f"  Total: {total}")
    print(f"  Used: {used}")
    print(f"  Available: {available}")
```

---

## 🔒 BẢO MẬT

### **Hardware ID Generation**
```
Hardware ID = SHA256(CPU_ID + Motherboard_Serial)[:32]
```

### **License Encryption**
- **Algorithm**: AES-256 (Fernet)
- **Key Derivation**: PBKDF2-HMAC-SHA256 (100,000 iterations)
- **Salt**: `miniZ_MCP_Professional_2025`
- **Unique per machine**: Key derived from Hardware ID

### **License File Location**
```
Windows: C:\Users\<user>\AppData\Local\miniZ_MCP\.license\license.enc
Linux: ~/.miniz_mcp/.license/license.enc
```

---

## 📞 HỖ TRỢ

### **Liên Hệ**
- **Email**: support@miniz-mcp.com
- **Website**: https://miniz-mcp.com

### **Documentation**
- **Full API**: `https://docs.miniz-mcp.com/license`
- **GitHub**: `https://github.com/miniz-mcp/professional`

---

## ✅ CHECKLIST PHÂN PHỐI

Khi gửi cho khách hàng, đảm bảo:

- [ ] File installer: `miniZ_MCP_Professional_Setup_v4.3.0.exe`
- [ ] 1 License key (từ tier phù hợp)
- [ ] File hướng dẫn này: `LICENSE_ACTIVATION_GUIDE.md`
- [ ] Ghi nhận key đã gửi vào `LICENSE_TRACKING.json`
- [ ] Email xác nhận gửi khách hàng

---

**🎉 Chúc mừng! Hệ thống license bảo mật cao đã sẵn sàng phân phối!**
