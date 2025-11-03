# 🚀 Xiaozhi MCP Control Panel

**Phần mềm điều khiển máy tính thông minh qua AI - Model Context Protocol**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 📋 Tổng quan

Xiaozhi MCP Control Panel là phần mềm điều khiển máy tính Windows toàn diện thông qua giao thức MCP (Model Context Protocol), cho phép AI điều khiển máy tính của bạn với **35+ công cụ** mạnh mẽ.

### ✨ Tính năng chính

#### 🎛️ Điều khiển hệ thống (15 công cụ)
- Điều chỉnh âm lượng, độ sáng màn hình
- Chụp màn hình, hiển thị thông báo
- Khóa máy tính, tắt/khởi động lại
- Xem tài nguyên hệ thống (CPU, RAM, Disk)
- Quản lý clipboard, hoàn tác thao tác
- Thay đổi theme Windows, đổi hình nền

#### 📁 Quản lý File & Process (7 công cụ)
- Mở ứng dụng, tạo/đọc file
- Liệt kê files trong thư mục
- Xem danh sách tiến trình đang chạy
- Tắt tiến trình theo tên hoặc PID
- Kiểm tra dung lượng ổ đĩa

#### 🎵 Thư viện nhạc thông minh (4 công cụ)
- Tự động phát nhạc từ thư mục `music_library/`
- Tìm kiếm và phát nhạc theo từ khóa
- Hỗ trợ tổ chức theo thư mục con (Pop, Rock, etc.)
- Điều khiển Windows Media Player

#### 🌐 Truy cập Web & YouTube (6 công cụ)
- Mở nhanh: YouTube, Facebook, Google, TikTok
- Tìm kiếm Google, YouTube
- Điều khiển YouTube player (play/pause, tua, âm lượng)
- Mở bất kỳ website nào

#### 📰 Tin tức & Thông tin (3 công cụ)
- Đọc tin tức VnExpress theo chủ đề
- Tìm kiếm tin tức
- **Giá vàng real-time** từ GiaVang.org (SJC, DOJI, PNJ)

---

## 🚀 Cài đặt nhanh

### Yêu cầu hệ thống
- Windows 10/11
- Python 3.8 trở lên
- Kết nối Internet

### Cài đặt tự động

1. **Chạy file INSTALL.bat**
   ```
   Nhấp đúp vào INSTALL.bat
   ```
   Script sẽ tự động:
   - Kiểm tra Python
   - Cài đặt dependencies (FastAPI, websockets, BeautifulSoup4, etc.)
   - Tạo thư mục music_library

2. **Lấy Xiaozhi Token**
   - Truy cập: https://xiaozhi.me
   - Đăng nhập và lấy JWT token từ profile

3. **Khởi động**
   ```
   Nhấp đúp vào START.bat
   ```
   - Server sẽ khởi động tại http://localhost:8000
   - Trình duyệt tự động mở Dashboard

4. **Cấu hình Token**
   - Click icon ⚙️ góc phải trên Dashboard
   - Dán JWT token vào
   - Click "💾 Lưu"

---

## 📖 Hướng dẫn sử dụng

### Dashboard Web (http://localhost:8000)

Interface gồm 3 phần:

1. **📊 Dashboard**: Xem tất cả 35 công cụ và thực thi nhanh
2. **🛠️ Công Cụ**: Giao diện chi tiết cho từng công cụ
3. **📋 Log**: Xem lịch sử hoạt động

### Sử dụng qua AI (Xiaozhi)

Sau khi kết nối thành công, bạn có thể ra lệnh cho AI:

**Ví dụ:**
- "Đặt âm lượng 50%"
- "Chụp màn hình"
- "Phát nhạc pop"
- "Mở YouTube tìm nhạc remix"
- "Cho tôi tin tức mới nhất"
- "Giá vàng hôm nay"
- "Khóa máy tính"

---

## 📂 Cấu trúc thư mục

```
miniz_pctool/
├── xiaozhi_final.py          # Chương trình chính
├── requirements.txt          # Dependencies
├── xiaozhi_endpoints.json    # Cấu hình token (tự tạo)
├── music_library/            # Thư mục nhạc
│   ├── Pop/
│   ├── Rock/
│   └── [Các file .mp3, .wav, .flac...]
├── INSTALL.bat               # Script cài đặt
├── START.bat                 # Script khởi động
├── CHECK.bat                 # Kiểm tra cài đặt
├── CREATE_SHORTCUT.bat       # Tạo shortcut desktop
├── README.md                 # File này
├── QUICKSTART.md             # Hướng dẫn nhanh
├── CHANGELOG.md              # Lịch sử phiên bản
├── MUSIC_GUIDE.md            # Hướng dẫn thư viện nhạc
└── LICENSE                   # Giấy phép MIT
```

---

## 🎵 Thư viện nhạc

### Thêm nhạc
1. Copy file nhạc (.mp3, .wav, .flac, .m4a) vào `music_library/`
2. Có thể tạo thư mục con để phân loại:
   ```
   music_library/
   ├── Pop/
   ├── Rock/
   ├── EDM/
   └── Ballad/
   ```

### Sử dụng
- **List**: "Liệt kê nhạc" → Tự động phát bài đầu tiên
- **Search**: "Tìm nhạc có love" → Phát bài phù hợp
- **Play**: "Phát In Love.mp3"
- **Stop**: "Dừng nhạc"

Chi tiết: Xem [MUSIC_GUIDE.md](MUSIC_GUIDE.md)

---

## 🔧 Troubleshooting

### Server không khởi động
```bash
# Kiểm tra Python
python --version

# Kiểm tra dependencies
pip list

# Cài lại dependencies
pip install -r requirements.txt --force-reinstall
```

### Không kết nối được Xiaozhi
1. Kiểm tra token có đúng không
2. Kiểm tra kết nối internet
3. Xem log trong Dashboard → Tab "Log"

### Nhạc không phát
1. Kiểm tra file nhạc trong `music_library/`
2. Đảm bảo Windows Media Player đã cài đặt
3. Thử mở file nhạc thủ công để test

### Lỗi module
```bash
pip install fastapi uvicorn websockets beautifulsoup4 requests feedparser pyautogui pillow psutil pycaw comtypes --upgrade
```

---

## 📞 Hỗ trợ

- **Issues**: [GitHub Issues](https://github.com/nguyenconghuy2904-source/miniz_pc_toolfix/issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)

---

## 📄 Giấy phép

MIT License - Xem [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 🎯 Phiên bản hiện tại: v4.0.0

**Cập nhật mới nhất:**
- ✅ 35+ công cụ điều khiển máy tính
- ✅ Thư viện nhạc tự động với auto-play
- ✅ Giá vàng real-time từ GiaVang.org
- ✅ Dashboard UI hiện đại với sidebar
- ✅ Multi-device endpoint support
- ✅ YouTube controls với keyboard shortcuts
- ✅ Tin tức VnExpress theo chủ đề

---

**Made with ❤️ for Xiaozhi MCP**
