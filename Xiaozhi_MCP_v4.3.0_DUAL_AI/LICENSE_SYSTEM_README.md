# miniZ MCP v4.3.0 - Professional Edition
## Hệ Thống License Chuyên Nghiệp

---

## 🎯 TỔNG QUAN

miniZ MCP v4.3.0 Professional Edition sử dụng hệ thống license key với hardware binding để bảo vệ bản quyền. Mỗi license key chỉ có thể kích hoạt trên SỐ LƯỢNG GIỚI HẠN máy tính (mặc định: 1 máy).

## 🔑 CÁC LOẠI LICENSE

### 1. **Trial** (Dùng thử)
- Thời hạn: 30 ngày
- Số thiết bị: 1 máy
- Đầy đủ tính năng
- Phù hợp: Khách hàng muốn dùng thử

### 2. **Standard** (Tiêu chuẩn)
- Thời hạn: 1 năm
- Số thiết bị: 1 máy
- Đầy đủ tính năng
- Phù hợp: Cá nhân, freelancer

### 3. **Professional** (Chuyên nghiệp)
- Thời hạn: 1 năm
- Số thiết bị: 1 máy
- Ưu tiên hỗ trợ
- Phù hợp: Công ty nhỏ

### 4. **Enterprise** (Doanh nghiệp)
- Thời hạn: 1 năm
- Số thiết bị: 5-10 máy (tùy chỉnh)
- Hỗ trợ VIP
- Phù hợp: Công ty lớn

---

## 📋 HƯỚNG DẪN ADMIN

### Tạo License Key Mới

```bash
cd "f:\miniz_pctool - Copy\Xiaozhi_MCP_v4.3.0_DUAL_AI"
python license_generator.py
```

Menu sẽ hiển thị:
```
1. Tạo license mới
2. Xem danh sách license
3. Kiểm tra license cụ thể
4. Vô hiệu hóa license
5. Gỡ kích hoạt thiết bị
0. Thoát
```

### Ví dụ tạo license:

**Tạo license Standard cho khách hàng:**
```
Chọn: 1
Tên khách hàng: Nguyen Van A
Loại: 2 (Standard)
Số ngày: 365
Ghi chú: Khách hàng VIP
```

Hệ thống sẽ tạo license key dạng:
```
A2K9-7XM4-P5N8-Q3W1
```

### Database License

Tất cả license được lưu trong file: `license_database.json`

**Cấu trúc:**
```json
{
  "licenses": {
    "A2K9-7XM4-P5N8-Q3W1": {
      "customer_name": "Nguyen Van A",
      "license_type": "standard",
      "created_at": "2025-11-27T10:30:00",
      "expires_at": "2026-11-27T10:30:00",
      "max_devices": 1,
      "activated_devices": [
        "F4A9B2C1D8E5F3A7B4C9D2E6F1A8B3C5"
      ],
      "status": "active"
    }
  }
}
```

---

## 🚀 HƯỚNG DẪN KHÁCH HÀNG

### Cài Đặt

1. **Download miniZ MCP v4.3.0**
2. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy chương trình:**
   ```bash
   python xiaozhi_final.py
   ```

### Kích Hoạt License

Khi chạy lần đầu, cửa sổ activation sẽ hiện:

![Activation Window](activation_preview.png)

**Các bước:**

1. **Copy Hardware ID** (nút 📋 Copy Hardware ID)
2. **Gửi Hardware ID cho Admin** để nhận license key
3. **Nhập License Key** vào ô (format: XXXX-XXXX-XXXX-XXXX)
4. **Click "✅ Kích Hoạt"**

**Chế độ Offline:**
- Nếu máy không có internet, tick ☑️ "Chế độ Offline"
- Hệ thống sẽ kích hoạt local (không verify với server)

### Lưu Ý Quan Trọng ⚠️

1. **Mỗi license key CHỈ dùng cho SỐ LƯỢNG MÁY GIỚI HẠN**
   - Standard/Professional: 1 máy
   - Enterprise: 5-10 máy (tùy gói)

2. **Hardware ID tự động sinh dựa trên:**
   - CPU ID
   - Motherboard Serial
   - Machine info

3. **Thay đổi phần cứng = Hardware ID mới**
   - Nếu đổi mainboard/CPU → Cần deactivate license cũ

4. **Chuyển sang máy mới:**
   - Liên hệ Admin để deactivate thiết bị cũ
   - Admin dùng option "5. Gỡ kích hoạt thiết bị"
   - Sau đó có thể activate trên máy mới

---

## 🔧 XỬ LÝ SỰ CỐ

### Lỗi: "License key đã được kích hoạt trên máy khác"

**Nguyên nhân:**
- License đã dùng hết slot thiết bị
- Hoặc đang kích hoạt trên máy khác

**Giải pháp:**
1. Liên hệ Admin
2. Cung cấp:
   - License key
   - Hardware ID máy cũ (nếu có)
   - Hardware ID máy mới
3. Admin sẽ deactivate máy cũ

### Lỗi: "License đã hết hạn"

**Giải pháp:**
- Liên hệ Admin để gia hạn
- Admin tạo license key mới

### Lỗi: "Không kết nối được server"

**Giải pháp:**
- Tick ☑️ "Chế độ Offline"
- Hoặc kiểm tra internet

---

## 📊 THỐNG KÊ & BÁO CÁO

### Xem danh sách license đang active:

```bash
python license_generator.py
Chọn: 2
```

### Kiểm tra chi tiết 1 license:

```bash
python license_generator.py
Chọn: 3
Nhập license key: A2K9-7XM4-P5N8-Q3W1
```

Output:
```
✅ Tìm thấy license:
Khách hàng: Nguyen Van A
Loại: standard
Trạng thái: active
Tạo lúc: 2025-11-27T10:30:00
Hết hạn: 2026-11-27T10:30:00
Thiết bị kích hoạt: 1/1
Hardware IDs:
  - F4A9B2C1D8E5F3A7B4C9D2E6F1A8B3C5
```

---

## 🌐 LICENSE SERVER (Optional)

Hiện tại, hệ thống có thể hoạt động:
1. **Offline Mode:** Không cần server (dùng local database)
2. **Online Mode:** Kết nối server để verify realtime

Để bật Online Mode, cần:
1. Tạo REST API server tại: `https://api.miniz-mcp.com/license/verify`
2. API nhận request:
   ```json
   {
     "license_key": "A2K9-7XM4-P5N8-Q3W1",
     "hardware_id": "F4A9...",
     "product": "miniZ_MCP_v4.3.0",
     "action": "activate"
   }
   ```
3. API trả về:
   ```json
   {
     "success": true,
     "expires_at": "2026-11-27T10:30:00",
     "license_type": "standard",
     "customer_name": "Nguyen Van A"
   }
   ```

---

## 📞 HỖ TRỢ

- **Email:** support@miniz-mcp.com
- **Discord:** discord.gg/miniz-mcp
- **Documentation:** https://docs.miniz-mcp.com

---

## ⚖️ BẢN QUYỀN

© 2025 miniZ Team. All Rights Reserved.

Phần mềm được bảo vệ bởi license key và hardware binding.
Không được phép:
- Crack, reverse engineer
- Chia sẻ license key
- Sử dụng trên nhiều máy vượt giới hạn

Vi phạm sẽ bị thu hồi license và xử lý theo pháp luật.

---

**Version:** 4.3.0 Professional Edition  
**Last Updated:** November 27, 2025
