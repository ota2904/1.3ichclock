# ⚖️ ĐIỀU KHOẢN & MIỄN TRÁCH NHIỆM

## 📋 THÔNG TIN SẢN PHẨM

**Tên phần mềm:** Xiaozhi MCP Control Panel  
**Phiên bản:** v4.3.0 Dual AI Edition  
**Nhà phát triển:** miniZ Team  
**Loại giấy phép:** MIT License (Mã nguồn mở)  
**Ngày phát hành:** Tháng 11/2025  

---

## ⚠️ ĐIỀU KHOẢN SỬ DỤNG

### 1. CHẤP NHẬN ĐIỀU KHOẢN
Bằng việc tải xuống, cài đặt và sử dụng phần mềm Xiaozhi MCP Control Panel, bạn đồng ý với tất cả các điều khoản và điều kiện sau đây. Nếu không đồng ý, vui lòng không sử dụng phần mềm.

### 2. PHẠM VI SỬ DỤNG
- ✅ **Được phép:** Sử dụng cá nhân, phi thương mại
- ✅ **Được phép:** Chỉnh sửa code cho mục đích cá nhân
- ✅ **Được phép:** Chia sẻ với bạn bè (phi thương mại)
- ❌ **KHÔNG được phép:** Bán lại hoặc sử dụng thương mại
- ❌ **KHÔNG được phép:** Xóa credit/logo của tác giả
- ❌ **KHÔNG được phép:** Phân phối dưới tên người khác

### 3. YÊU CẦU HỆ THỐNG
- **Hệ điều hành:** Windows 10/11 (64-bit)
- **Python:** 3.8 trở lên
- **RAM:** Tối thiểu 4GB
- **Kết nối:** Internet (để sử dụng AI và MCP)

### 4. QUYỀN TRUY CẬP HỆ THỐNG
Phần mềm yêu cầu các quyền sau để hoạt động:
- 🔊 **Âm lượng hệ thống:** Điều chỉnh volume, mute/unmute
- 📸 **Chụp màn hình:** Mở công cụ Snipping Tool
- 🔒 **Khóa máy tính:** Lock/shutdown/restart
- 📁 **Đọc/ghi file:** Tạo, đọc, xóa file theo lệnh
- ⚙️ **Quản lý tiến trình:** Xem và tắt tiến trình
- 🌐 **Kết nối Internet:** Gọi API AI (Gemini, GPT-4) và MCP

**LƯU Ý QUAN TRỌNG:** Phần mềm chỉ thực thi lệnh khi người dùng chủ động yêu cầu thông qua AI hoặc Web UI. Không có hoạt động nền không xin phép.

---

## 🛡️ MIỄN TRÁCH NHIỆM

### 1. TRÁCH NHIỆM NGƯỜI DÙNG
Người dùng chịu toàn bộ trách nhiệm về:
- ✔️ Việc sử dụng phần mềm đúng mục đích
- ✔️ Bảo mật thông tin cá nhân (JWT token, API keys)
- ✔️ Hậu quả từ các lệnh thực thi (xóa file, tắt tiến trình, v.v.)
- ✔️ Chi phí phát sinh từ API trả phí (OpenAI GPT-4)

### 2. MIỄN TRỪ TRÁCH NHIỆM CỦA NHÀ PHÁT TRIỂN
Nhà phát triển **KHÔNG chịu trách nhiệm** về:
- ❌ Mất mát dữ liệu do sử dụng sai
- ❌ Lỗi phần mềm gây ảnh hưởng đến hệ thống
- ❌ Chi phí API keys của bên thứ ba (OpenAI, Google)
- ❌ Thiệt hại gián tiếp hoặc trực tiếp từ việc sử dụng phần mềm
- ❌ Xung đột với phần mềm khác trên hệ thống
- ❌ Vấn đề bảo mật nếu người dùng chia sẻ token/API key

### 3. BẢO MẬT THÔNG TIN
- 🔐 **JWT Token & API Keys:** Được lưu LOCAL trên máy người dùng (`xiaozhi_endpoints.json`)
- 🔐 **Không thu thập dữ liệu:** Phần mềm không gửi bất kỳ thông tin cá nhân nào về server của tác giả
- 🔐 **Kết nối AI:** Chỉ gửi prompt đến API của Google Gemini và OpenAI (nếu user cấu hình)
- ⚠️ **LƯU Ý:** User phải tự bảo vệ file `xiaozhi_endpoints.json` chứa token/API keys

### 4. ĐIỀU KHOẢN VỀ AI
#### Google Gemini (MIỄN PHÍ)
- Giới hạn: 1500 requests/ngày (theo chính sách Google)
- Chịu sự điều chỉnh của Google AI Studio Terms of Service
- Link: https://ai.google.dev/gemini-api/terms

#### OpenAI GPT-4 (TRẢ PHÍ)
- Chi phí: $0.01-0.03/1K tokens (người dùng tự thanh toán)
- Chịu sự điều chỉnh của OpenAI Terms of Service
- Link: https://openai.com/policies/terms-of-use
- Người dùng tự chịu trách nhiệm về chi phí API

### 5. KHÔNG BẢO HÀNH
Phần mềm được cung cấp **"AS IS"** (nguyên trạng) mà không có bất kỳ bảo hành nào, bao gồm:
- ❌ Không đảm bảo hoạt động 100% không lỗi
- ❌ Không đảm bảo tương thích với mọi cấu hình
- ❌ Không đảm bảo hiệu suất trên mọi hệ thống
- ❌ Không cam kết hỗ trợ kỹ thuật 24/7

### 6. GIỚI HẠN TRÁCH NHIỆM PHÁP LÝ
Trong mọi trường hợp, nhà phát triển và các bên liên quan **KHÔNG chịu trách nhiệm** về:
- Bất kỳ thiệt hại trực tiếp, gián tiếp, ngẫu nhiên, đặc biệt hoặc hệ quả
- Mất dữ liệu, mất lợi nhuận, gián đoạn kinh doanh
- Thiệt hại vượt quá giá trị phần mềm (FREE)

---

## 📜 GIẤY PHÉP MÃ NGUỒN

### MIT License (Tóm tắt)
```
Copyright (c) 2025 miniZ Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to use, copy, modify, merge, publish, distribute, sublicense
for PERSONAL/NON-COMMERCIAL purposes only.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

**Chi tiết đầy đủ:** Xem file `LICENSE` trong package

---

## 🔒 BẢO MẬT & QUYỀN RIÊNG TƯ

### Thu Thập Dữ Liệu
Phần mềm **KHÔNG thu thập** các thông tin sau:
- ❌ Thông tin cá nhân (tên, email, địa chỉ)
- ❌ Lịch sử sử dụng
- ❌ Nội dung lệnh/prompt gửi cho AI
- ❌ File hệ thống
- ❌ Screenshot/clipboard content

### Kết Nối Bên Ngoài
Phần mềm chỉ kết nối đến:
1. **api.xiaozhi.me** - Model Context Protocol server (WebSocket)
2. **generativelanguage.googleapis.com** - Google Gemini API (nếu dùng)
3. **api.openai.com** - OpenAI GPT-4 API (nếu dùng)

**LƯU Ý:** Nội dung prompt gửi cho AI sẽ được xử lý bởi Google/OpenAI theo chính sách của họ.

---

## ⚠️ CẢNH BÁO AN TOÀN

### 1. Không Sử Dụng Phần Mềm Để
- ❌ Xâm nhập trái phép vào hệ thống khác
- ❌ Phá hoại, gây thiệt hại cho người khác
- ❌ Vi phạm pháp luật hoặc quyền riêng tư
- ❌ Tự động hóa các hành vi spam/abuse

### 2. Khuyến Nghị An Toàn
- ✅ Backup dữ liệu quan trọng trước khi sử dụng
- ✅ Chỉ cấp API key cho tài khoản cá nhân
- ✅ Đọc kỹ prompt trước khi xác nhận lệnh nguy hiểm (xóa file, shutdown)
- ✅ Không chia sẻ file `xiaozhi_endpoints.json` chứa token

### 3. Lệnh Nguy Hiểm Cần Thận Trọng
- 🔥 `kill_process` - Tắt tiến trình (có thể gây crash hệ thống)
- 🔥 `shutdown_schedule` - Tắt máy/khởi động lại
- 🔥 `create_file`, `read_file` - Đọc/ghi file nhạy cảm
- 🔥 `lock_computer` - Khóa màn hình ngay lập tức

---

## 📞 HỖ TRỢ & LIÊN HỆ

### Kênh Chính Thức
- 🎥 **YouTube:** https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU
- 📧 **Email hỗ trợ:** (Xem trong video YouTube)

### Báo Lỗi (Bug Report)
Nếu phát hiện lỗi, vui lòng gửi thông tin:
1. Phiên bản phần mềm (v4.3.0)
2. Hệ điều hành (Windows 10/11)
3. Mô tả lỗi chi tiết
4. Log lỗi (nếu có)

**LƯU Ý:** Hỗ trợ kỹ thuật là MIỄN PHÍ nhưng không cam kết thời gian phản hồi.

---

## 📝 CẬP NHẬT ĐIỀU KHOẢN

Nhà phát triển có quyền cập nhật điều khoản này bất kỳ lúc nào mà không cần thông báo trước. Phiên bản mới nhất sẽ được công bố trên:
- GitHub Repository (nếu công khai)
- Kênh YouTube miniZ

**Ngày cập nhật cuối:** 16/11/2025

---

## ✅ XÁC NHẬN ĐỒNG Ý

Bằng việc sử dụng phần mềm, bạn xác nhận rằng:
- [x] Đã đọc và hiểu toàn bộ điều khoản trên
- [x] Đồng ý chịu trách nhiệm về việc sử dụng phần mềm
- [x] Không yêu cầu nhà phát triển chịu trách nhiệm về thiệt hại
- [x] Sử dụng đúng mục đích và tuân thủ pháp luật

---

## 📄 KẾT LUẬN

Xiaozhi MCP Control Panel là công cụ mạnh mẽ để điều khiển máy tính qua AI. Sử dụng có trách nhiệm và an toàn!

**Cảm ơn bạn đã tin tưởng sử dụng sản phẩm của miniZ Team! 🙏**

---

*Tài liệu này có giá trị pháp lý và là một phần không thể tách rời của package phần mềm.*
