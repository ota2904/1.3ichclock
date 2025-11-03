# ⚡ Quick Start Guide - Xiaozhi MCP Control Panel

Hướng dẫn nhanh để bắt đầu sử dụng Xiaozhi MCP Control Panel trong 5 phút!

---

## 📦 Bước 1: Cài đặt (2 phút)

### Cài đặt tự động
```
Nhấp đúp vào INSTALL.bat
```

Script sẽ tự động:
1. ✅ Kiểm tra Python đã cài chưa
2. ✅ Cài đặt tất cả dependencies
3. ✅ Tạo thư mục music_library
4. ✅ Sẵn sàng sử dụng

### Cài đặt thủ công (nếu cần)
```bash
pip install -r requirements.txt
```

Dependencies:
- fastapi
- uvicorn
- websockets
- beautifulsoup4
- requests
- feedparser
- pyautogui
- pillow
- psutil
- pycaw
- comtypes

---

## 🔑 Bước 2: Lấy Xiaozhi Token (1 phút)

1. Truy cập: https://xiaozhi.me
2. Đăng nhập (Google/Email)
3. Vào Profile → MCP Settings
4. Copy JWT token (dạng: eyJhbGciOiJIUzI1NiIs...)

**Lưu ý**: Token này là duy nhất và bảo mật. Không chia sẻ với người khác.

---

## 🚀 Bước 3: Khởi động Server (30 giây)

```
Nhấp đúp vào START.bat
```

Hoặc chạy thủ công:
```bash
python xiaozhi_final.py
```

**Kết quả:**
- ✅ Server khởi động tại: http://localhost:8000
- ✅ Trình duyệt tự động mở Dashboard
- ✅ Hiển thị 35 công cụ có sẵn

---

## ⚙️ Bước 4: Cấu hình Token (1 phút)

### Cách 1: Qua Dashboard UI
1. Mở http://localhost:8000
2. Click icon ⚙️ ở góc phải trên
3. Dán JWT token vào ô "Endpoint"
4. Click "💾 Lưu"
5. Đợi kết nối (status chuyển sang "Connected")

### Cách 2: Qua file JSON (Advanced)
Tạo/sửa file `xiaozhi_endpoints.json`:
```json
[
  {
    "name": "Thiết bị 1",
    "token": "",
    "enabled": false
  },
  {
    "name": "Thiết bị 2",
    "token": "",
    "enabled": false
  },
  {
    "name": "Thiết bị 3",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "enabled": true
  }
]
```

---

## 🎉 Bước 5: Test thử (1 phút)

### Test qua Dashboard
1. Vào tab "📊 Dashboard"
2. Click "🔊 Điều Chỉnh Âm Lượng"
3. Đặt volume = 50
4. Click "Đặt âm lượng"
5. ✅ Âm lượng thay đổi thành công!

### Test qua Xiaozhi AI
Nói với Xiaozhi:
- "Đặt âm lượng 70%"
- "Chụp màn hình"
- "Cho tôi biết thời gian"

✅ Nếu thành công → Bạn đã sẵn sàng!

---

## 📚 Sử dụng nâng cao

### 🎵 Thư viện nhạc

#### Thêm nhạc
1. Copy file nhạc vào: `music_library/`
2. Phân loại theo thư mục (tùy chọn):
   ```
   music_library/
   ├── Pop/
   │   ├── song1.mp3
   │   └── song2.mp3
   ├── Rock/
   │   └── song3.mp3
   └── song4.mp3
   ```

#### Sử dụng
**Qua AI:**
- "Liệt kê nhạc" → Auto-play bài đầu
- "Phát nhạc pop" → Phát từ folder Pop/
- "Tìm nhạc có love" → Search và play
- "Dừng nhạc"

**Qua Dashboard:**
- Tab "Công Cụ" → Tab thứ 2 (nếu có)
- Hoặc dùng Quick Actions

Chi tiết: [MUSIC_GUIDE.md](MUSIC_GUIDE.md)

---

### 📰 Tin tức VnExpress

**Lấy tin tức:**
- "Cho tôi tin tức mới nhất"
- "Tin tức thể thao"
- "Tin kinh doanh"

**Chủ đề có sẵn:**
- home (mới nhất)
- thoi-su (thời sự)
- the-gioi (thế giới)
- kinh-doanh
- giai-tri
- the-thao
- phap-luat
- giao-duc
- suc-khoe
- du-lich
- khoa-hoc
- so-hoa
- xe

---

### 💰 Giá vàng Real-time

**Sử dụng:**
- "Giá vàng hôm nay"
- "Cho tôi biết giá vàng SJC"

**Nguồn:** GiaVang.org (cập nhật real-time)

**Loại vàng:**
- Vàng SJC
- Vàng DOJI
- Vàng PNJ
- Và nhiều loại khác...

---

### 🌐 YouTube & Website

**Mở website:**
- "Mở YouTube"
- "Mở YouTube tìm nhạc remix"
- "Mở Facebook"
- "Mở Google"
- "Mở github.com"

**Điều khiển YouTube:**
(Yêu cầu: tab YouTube phải đang active)
- "Tạm dừng YouTube"
- "Tua 10 giây"
- "Tăng âm lượng YouTube"
- "Tắt tiếng YouTube"

---

## 🛠️ Troubleshooting nhanh

### ❌ Server không khởi động
```bash
# Kiểm tra Python
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Kiểm tra port 8000 có bị chiếm không
netstat -ano | findstr :8000
```

### ❌ Status "Disconnected"
1. ✅ Kiểm tra token đã dán đúng chưa
2. ✅ Kiểm tra internet
3. ✅ Xem log trong tab "📋 Log"
4. ✅ Thử token mới từ xiaozhi.me

### ❌ Nhạc không phát
1. ✅ Kiểm tra file nhạc trong `music_library/`
2. ✅ Đảm bảo Windows Media Player đã cài
3. ✅ Test mở file nhạc thủ công
4. ✅ Kiểm tra định dạng file (.mp3, .wav, .flac, .m4a)

### ❌ YouTube controls không hoạt động
1. ✅ Tab YouTube phải đang active (focus)
2. ✅ Đảm bảo đang phát video
3. ✅ Thử lại với video khác
4. ✅ Kiểm tra keyboard shortcuts của browser

---

## 📁 File quan trọng

```
📂 miniz_pctool/
│
├── 🚀 START.bat              # Khởi động nhanh
├── 📦 INSTALL.bat            # Cài đặt
├── ✅ CHECK.bat              # Kiểm tra cài đặt
├── 🔗 CREATE_SHORTCUT.bat   # Tạo shortcut desktop
│
├── 🐍 xiaozhi_final.py      # Chương trình chính
├── 📋 requirements.txt      # Dependencies
├── ⚙️ xiaozhi_endpoints.json # Config token (tự tạo)
│
├── 📖 README.md             # Tài liệu chính
├── ⚡ QUICKSTART.md         # File này
├── 📝 CHANGELOG.md          # Lịch sử phiên bản
├── 🎵 MUSIC_GUIDE.md        # Hướng dẫn nhạc
└── 📜 LICENSE               # Giấy phép MIT
```

---

## 💡 Tips & Tricks

### Tạo Shortcut Desktop
```
Nhấp đúp CREATE_SHORTCUT.bat
```
→ Tạo shortcut "Xiaozhi MCP" trên desktop để khởi động nhanh

### Tự động khởi động cùng Windows
1. Nhấn `Win + R`
2. Gõ: `shell:startup`
3. Copy shortcut "Xiaozhi MCP" vào folder này

### Kiểm tra cài đặt
```
Nhấp đúp CHECK.bat
```
→ Kiểm tra Python, dependencies, và cấu hình

### Multi-device support
Bạn có thể cấu hình 3 thiết bị khác nhau:
1. Máy tính cá nhân
2. Máy tính công việc
3. Laptop

Chuyển đổi qua Dashboard → Tab "Cấu hình"

---

## 🎯 Các lệnh hay dùng

### Hệ thống
- "Đặt âm lượng 50%"
- "Chụp màn hình"
- "Khóa máy tính"
- "Tắt máy sau 60 giây"
- "Độ sáng 70%"
- "Đổi theme tối"

### File & Process
- "Mở notepad"
- "Mở calculator"
- "Liệt kê tiến trình"
- "Tắt tiến trình chrome"
- "Tạo file test.txt"
- "Đọc file test.txt"

### Web & Media
- "Mở YouTube tìm nhạc chill"
- "Mở Facebook"
- "Tìm Google về Python"
- "Phát nhạc pop"
- "Dừng nhạc"

### Thông tin
- "Thời gian hiện tại"
- "Tin tức mới nhất"
- "Giá vàng hôm nay"
- "Trạng thái pin"
- "Thông tin mạng"

---

## 📞 Hỗ trợ

- **Kênh YouTube miniZ**: [https://youtube.com/@minizjp](https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU)
- **Documentation**: [README.md](README.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

---

## 🎓 Tài nguyên

- **Xiaozhi**: https://xiaozhi.me
- **MCP Protocol**: https://modelcontextprotocol.io/
- **FastAPI**: https://fastapi.tiangolo.com/

---

**🎉 Chúc bạn sử dụng Xiaozhi MCP Control Panel thành công!**

*Nếu gặp vấn đề, hãy kiểm tra tab "Log" trong Dashboard hoặc liên hệ qua kênh YouTube miniZ.*
