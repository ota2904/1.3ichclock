# ⚡ Quick Start - Hướng Dẫn Nhanh

## 🚀 Cài Đặt & Chạy (3 Bước)

### Bước 1: Cài Đặt Tự Động
```bash
# Chạy file cài đặt (sẽ tự động cài tất cả)
INSTALL.bat
```

**INSTALL.bat sẽ tự động:**
- ✅ Kiểm tra Python
- ✅ Cài đặt tất cả thư viện cần thiết
- ✅ Khởi động server ngay sau khi cài xong

### Bước 2: Lấy JWT Token
1. Truy cập: https://dash.upx8.com
2. Đăng nhập tài khoản Xiaozhi
3. Tạo MCP Endpoint
4. Copy JWT token (dạng: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9...)

### Bước 3: Cấu Hình Token
1. Mở trình duyệt: http://localhost:8000
2. Click tab **⚙️ Cấu Hình**
3. Dán JWT token vào **Thiết bị 1**
4. Click **💾 Lưu**
5. ✅ Kết nối thành công!

---

## 🔄 Sử Dụng Hàng Ngày

### Khởi Động Nhanh
```bash
START.bat
```

### Dừng Server
Nhấn `Ctrl + C` trong terminal

### Khởi Động Lại
Đóng terminal và chạy lại `START.bat`

---

## 🛠️ Các File Quan Trọng

| File | Công Dụng |
|------|-----------|
| `INSTALL.bat` | Cài đặt lần đầu (chỉ chạy 1 lần) |
| `START.bat` | Khởi động server (dùng hàng ngày) |
| `xiaozhi_final.py` | File chính chứa code |
| `requirements.txt` | Danh sách thư viện |

---

## 📊 Dashboard

Sau khi khởi động, mở: **http://localhost:8000**

### 4 Tab Chính:
- **📊 Dashboard** - Tổng quan 30 tools
- **🛠️ Công Cụ** - Chi tiết từng tool
- **⚙️ Cấu Hình** - Quản lý thiết bị
- **📜 Log** - Xem hoạt động

---

## ❓ Xử Lý Lỗi

### Lỗi: "Python không tìm thấy"
**Giải pháp:**
1. Cài Python 3.13+ từ: https://python.org
2. Tích chọn "Add Python to PATH" khi cài
3. Khởi động lại máy tính
4. Chạy lại `INSTALL.bat`

### Lỗi: "Port 8000 đang được sử dụng"
**Giải pháp:**
```powershell
# Tắt tiến trình đang dùng port 8000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force

# Chạy lại
START.bat
```

### Lỗi: "Không kết nối được Xiaozhi"
**Giải pháp:**
1. Kiểm tra JWT token còn hạn không (token hết hạn sau 1 năm)
2. Lấy token mới từ https://dash.upx8.com
3. Cập nhật token trong tab Cấu Hình
4. Click Lưu

### Lỗi: "Import Error"
**Giải pháp:**
```bash
# Cài lại thư viện
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 30 Tools Có Sẵn

### Hệ Thống (7)
- Volume, Screenshot, Notification, Resources
- Brightness, Lock, Shutdown Schedule

### File & Process (7)
- Open App, List/Kill Process
- Create/Read/List Files, Disk Usage

### Mạng & Web (3)
- Network Info, Battery, Web Search

### Tiện Ích (13)
- Calculator, Time, Clipboard (Get/Set)
- Sound, Desktop, Undo, Theme
- Wallpaper, Desktop Path, Paste, Enter, Find

---

## 🔗 Links Hữu Ích

- 🌐 Xiaozhi Dashboard: https://dash.upx8.com
- 📖 GitHub Repo: https://github.com/nguyenconghuy2904-source/miniz_pc_tool2
- 📚 MCP Docs: https://modelcontextprotocol.io

---

## 💡 Tips & Tricks

1. **Auto-start:** Tạo shortcut của `START.bat` vào thư mục Startup
2. **Multi-device:** Có thể cấu hình tới 3 thiết bị khác nhau
3. **Backup token:** Lưu JWT token vào file text để dùng lâu dài
4. **Check logs:** Tab Log cho biết tool nào đang chạy

---

## ✅ Checklist Cài Đặt

- [ ] Đã chạy `INSTALL.bat`
- [ ] Python 3.13+ đã cài
- [ ] Tất cả thư viện đã cài xong
- [ ] Server khởi động thành công
- [ ] Dashboard mở được ở localhost:8000
- [ ] Đã có JWT token từ Xiaozhi
- [ ] Đã lưu token trong tab Cấu Hình
- [ ] Thấy message "✅ Connected!" trong terminal
- [ ] Test thử 1 tool bất kỳ

🎉 **Hoàn thành! Bạn đã sẵn sàng sử dụng!**
