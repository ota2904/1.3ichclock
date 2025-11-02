# 🚀 Xiaozhi MCP Control Panel

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Bảng điều khiển Web hiện đại để kiểm soát máy tính Windows qua Xiaozhi MCP (Model Context Protocol) với **30 công cụ mạnh mẽ**.

![Dashboard](https://via.placeholder.com/800x400/7c3aed/ffffff?text=Xiaozhi+Control+Panel)

---

## ⚡ Cài Đặt Siêu Nhanh (3 Bước)

### 1️⃣ Cài Đặt Tự Động
```bash
INSTALL.bat
```
Script sẽ tự động cài Python packages và khởi động server!

### 2️⃣ Lấy JWT Token
- Truy cập: https://dash.upx8.com
- Tạo MCP Endpoint → Copy JWT token

### 3️⃣ Kết Nối
- Mở: http://localhost:8000
- Tab **Cấu Hình** → Dán token → **Lưu**

✅ **Xong!** Giờ bạn có thể điều khiển PC qua Xiaozhi AI!

📖 **Chi tiết:** Xem [QUICKSTART.md](QUICKSTART.md)

---

## ✨ Tính Năng

### 🛠️ 30 Công Cụ Mạnh Mẽ

#### 🖥️ Hệ Thống (7 tools)
- 🔊 **Điều chỉnh âm lượng** - Thay đổi âm lượng hệ thống (0-100)
- 📸 **Chụp màn hình** - Chụp ảnh màn hình
- 🔔 **Hiển thị thông báo** - Gửi thông báo Windows
- 💻 **Tài nguyên hệ thống** - Theo dõi CPU, RAM, Network
- 🔆 **Độ sáng màn hình** - Điều chỉnh độ sáng
- 🔒 **Khóa máy tính** - Khóa Windows ngay lập tức
- ⏰ **Lên lịch tắt máy** - Tắt máy/khởi động lại theo lịch

#### 📁 File & Process (7 tools)
- 🚀 **Mở ứng dụng** - Khởi động ứng dụng
- 📋 **Tiến trình đang chạy** - Liệt kê tiến trình
- ❌ **Tắt tiến trình** - Dừng tiến trình theo PID/tên
- 📄 **Tạo file mới** - Tạo file văn bản
- 📖 **Đọc file** - Đọc nội dung file
- 📂 **Liệt kê files** - Xem danh sách file
- 💾 **Thông tin đĩa** - Kiểm tra dung lượng ổ đĩa

#### 🌐 Mạng & Web (3 tools)
- 🌐 **Thông tin mạng** - Xem cấu hình mạng
- 🔋 **Thông tin pin** - Kiểm tra trạng thái pin
- 🔍 **Tìm kiếm Google** - Mở Google Search

#### 🎨 Tiện Ích & Tùy Chỉnh (13 tools)
- 🧮 **Máy tính** - Tính toán biểu thức Python
- ⏰ **Thời gian** - Lấy thời gian hiện tại
- 📋 **Lấy Clipboard** - Đọc nội dung clipboard
- 📝 **Đặt Clipboard** - Ghi vào clipboard
- 🔊 **Phát âm thanh** - Phát beep sound
- 🖥️ **Hiển thị Desktop** - Hiện desktop (Win+D)
- ↩️ **Hoàn tác** - Ctrl+Z
- 🎨 **Đổi Theme** - Chuyển theme sáng/tối Windows
- 🖼️ **Đổi hình nền** - Thay wallpaper từ API
- 📁 **Đường dẫn Desktop** - Lấy path Desktop
- 📋 **Dán nội dung** - Paste (Ctrl+V)
- ⏎ **Nhấn Enter** - Mô phỏng phím Enter
- 🔎 **Tìm trong tài liệu** - Ctrl+F search

## 🎯 Giao Diện

### Sidebar Navigation
- 📊 **Dashboard** - Tổng quan nhanh với 30 action cards
- 🛠️ **Công Cụ** - 4 tabs phân loại chi tiết
- ⚙️ **Cấu Hình** - Quản lý 3 thiết bị MCP
- 📜 **Log** - Real-time activity log

### Theme
- 🎨 Gradient purple (Xiaozhi branding)
- 🌈 8 màu action cards (blue, green, orange, red, purple, cyan, pink, indigo)
- 📱 Responsive design

---

## 📦 Cấu Trúc Dự Án

```
xiaozhi-mcp-panel/
├── 📄 xiaozhi_final.py      # File chính (1200+ lines)
├── 🚀 INSTALL.bat            # Cài đặt tự động
├── 🚀 START.bat              # Khởi động nhanh
├── 📖 QUICKSTART.md          # Hướng dẫn chi tiết
├── 📖 README.md              # File này
├── 📋 requirements.txt       # Dependencies
├── 📝 CHANGELOG.md           # Lịch sử phiên bản
└── 📜 LICENSE                # MIT License
```

---

## 🔄 Sử Dụng Hàng Ngày

### Khởi Động
```bash
START.bat
```

### Truy Cập Dashboard
```
http://localhost:8000
```

### Dừng Server
Nhấn `Ctrl + C` trong terminal

---

## 🛠️ 30 Tools Có Sẵn

<details>
<summary><b>🖥️ Hệ Thống (7 tools)</b></summary>

- 🔊 Điều chỉnh âm lượng
- 📸 Chụp màn hình  
- 🔔 Hiển thị thông báo
- 💻 Tài nguyên hệ thống
- 🔆 Độ sáng màn hình
- 🔒 Khóa máy tính
- ⏰ Lên lịch tắt máy
</details>

<details>
<summary><b>📁 File & Process (7 tools)</b></summary>

- 🚀 Mở ứng dụng
- 📋 Tiến trình đang chạy
- ❌ Tắt tiến trình
- � Tạo file mới
- � Đọc file
- � Liệt kê files
- � Thông tin đĩa
</details>

<details>
<summary><b>🌐 Mạng & Web (3 tools)</b></summary>

- 🌐 Thông tin mạng
- 🔋 Thông tin pin
- � Tìm kiếm Google
</details>

<details>
<summary><b>� Tiện Ích (13 tools)</b></summary>

- 🧮 Máy tính
- ⏰ Thời gian
- 📋 Lấy/Đặt Clipboard
- 🔊 Phát âm thanh
- �️ Hiển thị Desktop
- ↩️ Hoàn tác
- 🎨 Đổi Theme
- 🖼️ Đổi hình nền
- 📁 Đường dẫn Desktop
- 📋 Dán nội dung
- ⏎ Nhấn Enter
- � Tìm trong tài liệu
</details>

---

## 🎯 Yêu Cầu Hệ Thống

- **OS:** Windows 10/11
- **Python:** 3.13+
- **RAM:** 4GB+
- **Disk:** 100MB

---

## 📚 Tài Liệu

- 📖 [Quick Start Guide](QUICKSTART.md) - Hướng dẫn chi tiết
- 📝 [Changelog](CHANGELOG.md) - Lịch sử cập nhật
- 📜 [License](LICENSE) - MIT License

---

## 🎓 Tham Khảo

- [xiaozhi-MCPTools](https://github.com/ZhongZiTongXue/xiaozhi-MCPTools) - Reference project (60+ tools)
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
- [Xiaozhi Dashboard](https://dash.upx8.com) - Lấy JWT token

---

## 🤝 Đóng Góp

Contributions, issues và feature requests được chào đón!

1. Fork repo
2. Tạo branch (`git checkout -b feature/YourFeature`)
3. Commit (`git commit -m 'Add YourFeature'`)
4. Push (`git push origin feature/YourFeature`)
5. Mở Pull Request

---

## 📞 Support

- 🐛 [Issues](https://github.com/nguyenconghuy2904-source/miniz_pc_tool2/issues)
- 🌐 [Xiaozhi Dashboard](https://dash.upx8.com)
- 📖 [Documentation](QUICKSTART.md)

---

## ⭐ Show Support

Nếu project hữu ích, hãy cho một **Star** ⭐!

---

<p align="center">
Made with ❤️ using FastAPI + MCP + Xiaozhi AI
</p>

