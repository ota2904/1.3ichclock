# 🚀 Xiaozhi MCP Control Panel

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Bảng điều khiển Web hiện đại để kiểm soát máy tính Windows qua Xiaozhi MCP (Model Context Protocol).

![Dashboard](https://via.placeholder.com/800x400/7c3aed/ffffff?text=Xiaozhi+Control+Panel)

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

## 🚀 Cài Đặt Nhanh

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/xiaozhi-mcp-panel.git
cd xiaozhi-mcp-panel
```

### 2. Cài Dependencies
```bash
pip install -r requirements.txt
```

### 3. Chạy Server
```bash
# Windows
RUN.bat

# Hoặc dùng Python trực tiếp
python xiaozhi_final.py
```

### 4. Mở Dashboard
```
http://localhost:8000
```

## 🔌 Kết Nối Xiaozhi MCP

### Bước 1: Lấy JWT Token
1. Truy cập [Xiaozhi Dashboard](https://dash.upx8.com)
2. Đăng nhập tài khoản
3. Tạo MCP Endpoint mới
4. Copy JWT token

### Bước 2: Cấu Hình
1. Mở `http://localhost:8000`
2. Click tab **Cấu hình**
3. Dán JWT token vào **Thiết bị 1**
4. Click **Lưu**

### Bước 3: Kiểm Tra
Trong terminal sẽ thấy:
```
✅ [Xiaozhi] Connected! (Thiết bị 1)
📨 [initialize]
📨 [notifications/initialized]
📨 [tools/list]
```

## 📊 Kiến Trúc

```
xiaozhi_final.py (1200+ lines)
├── 🔧 Tool Implementations (30 async functions)
├── 📋 TOOLS Registry (MCP tool definitions)
├── 🌐 Xiaozhi WebSocket Client
│   ├── Auto-retry connection
│   ├── JWT authentication
│   └── MCP protocol handler
├── 🚀 FastAPI Application
│   ├── HTTP endpoints (/api/*)
│   ├── WebSocket endpoint (/ws)
│   └── Static HTML dashboard
└── 💻 Embedded HTML/CSS/JS (Single-file deployment)
```

## 🛡️ Yêu Cầu Hệ Thống

- **OS:** Windows 10/11
- **Python:** 3.13 trở lên
- **RAM:** Tối thiểu 4GB
- **Disk:** 100MB trống

## 🔧 API Endpoints

| Method | Endpoint | Mô Tả |
|--------|----------|-------|
| GET | `/` | Dashboard HTML |
| GET | `/api/resources` | System resources |
| POST | `/api/volume` | Set volume |
| POST | `/api/screenshot` | Take screenshot |
| POST | `/api/notification` | Show notification |
| GET | `/api/endpoints` | Get device configs |
| POST | `/api/endpoints` | Save device configs |
| WS | `/ws` | WebSocket updates |

## 📝 MCP Protocol

Tuân thủ [Model Context Protocol 2024-11-05](https://modelcontextprotocol.io/):
- ✅ JSON-RPC 2.0 over WebSocket
- ✅ initialize/initialized handshake
- ✅ tools/list for tool discovery
- ✅ tools/call for execution

## 🎓 Tham Khảo

Dự án lấy cảm hứng từ:
- [xiaozhi-MCPTools](https://github.com/ZhongZiTongXue/xiaozhi-MCPTools) - Reference implementation (60+ tools)
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP specification
- [FastAPI](https://fastapi.tiangolo.com/) - Modern async web framework

## 🐛 Known Issues

- ⚠️ Một số tools yêu cầu quyền Administrator
- ⚠️ pyautogui có thể bị chặn bởi antivirus
- ⚠️ Wallpaper API đôi khi timeout

## 🚀 Roadmap

- [ ] Thêm authentication cho dashboard
- [ ] Multi-language support (EN/VI/CN)
- [ ] Plugin system để mở rộng tools
- [ ] Mobile responsive optimization
- [ ] Docker deployment
- [ ] Thêm 20+ tools từ reference project

## 📜 License

MIT License - Xem [LICENSE](LICENSE) để biết thêm chi tiết.

## 🤝 Đóng Góp

Contributions, issues và feature requests đều được chào đón!

1. Fork dự án
2. Tạo branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📞 Support

- 🐛 [Issues](https://github.com/YOUR_USERNAME/xiaozhi-mcp-panel/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/xiaozhi-mcp-panel/discussions)
- 🌐 [Xiaozhi Dashboard](https://dash.upx8.com)
- 📖 [MCP Documentation](https://modelcontextprotocol.io/)

## ⭐ Show Your Support

Nếu dự án hữu ích, hãy cho một **Star** ⭐!

---

Made with ❤️ using FastAPI + MCP + Xiaozhi AI
