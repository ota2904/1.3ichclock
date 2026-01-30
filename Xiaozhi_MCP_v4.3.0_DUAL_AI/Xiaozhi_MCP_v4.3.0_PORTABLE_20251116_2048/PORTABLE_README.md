# 📦 Xiaozhi MCP v4.3.0 - PORTABLE EDITION

**Phiên bản đóng gói hoàn chỉnh để giao khách hàng**

---

## 🎯 GIỚI THIỆU

Package này chứa **phần mềm điều khiển máy tính qua AI hoàn chỉnh** với:
- ✅ **38 công cụ** điều khiển Windows
- ✅ **2 AI Engines:** Google Gemini (FREE) + OpenAI GPT-4 (PAID)
- ✅ **Thư viện nhạc** với auto-play
- ✅ **Dashboard Web UI** hiện đại
- ✅ **Tài liệu đầy đủ** bằng tiếng Việt
- ✅ **Điều khoản miễn trách nhiệm** rõ ràng

---

## 📂 CẤU TRÚC PACKAGE

```
Xiaozhi_MCP_v4.3.0_DUAL_AI/
│
├── 📄 README.md                    # Hướng dẫn chính (ĐỌC ĐẦU TIÊN)
├── 📄 PORTABLE_README.md           # File này (Giới thiệu package)
├── 📄 DISCLAIMER.md                # ⚠️ ĐIỀU KHOẢN MIỄN TRÁCH NHIỆM (BẮT BUỘC ĐỌC)
├── 📄 LICENSE                      # Giấy phép MIT
├── 📄 CHANGELOG.md                 # Lịch sử phiên bản
│
├── 🚀 INSTALL.bat                  # Cài đặt tự động (Chạy đầu tiên)
├── 🚀 START.bat                    # Khởi động phần mềm
├── 🔍 CHECK.bat                    # Kiểm tra cài đặt
├── 🔗 CREATE_SHORTCUT.bat          # Tạo shortcut desktop
│
├── 🐍 xiaozhi_final.py             # Code chính (4000+ dòng)
├── 📝 requirements.txt             # Dependencies Python
├── ⚙️ xiaozhi_endpoints.json      # File cấu hình (tự tạo khi chạy)
│
├── 📘 QUICKSTART.md                # Hướng dẫn nhanh
├── 📘 MUSIC_GUIDE.md               # Hướng dẫn thư viện nhạc
├── 📘 GEMINI_GUIDE.md              # Hướng dẫn Gemini AI
├── 📘 GPT4_GUIDE.md                # Hướng dẫn GPT-4 AI
├── 📘 HUONG_DAN_THONG_TIN_MOI.md   # Thông tin mới nhất
├── 📘 DUAL_AI_SUMMARY.txt          # Tóm tắt Dual AI
│
├── 🧪 TEST_GEMINI.bat              # Test Gemini API
│
└── 🎵 music_library/               # Thư viện nhạc (thêm file .mp3 vào đây)
    ├── Pop/
    ├── Rock/
    ├── Classical/
    ├── QUICKSTART_MUSIC.md
    └── README.md
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT (5 PHÚT)

### Bước 1: Kiểm tra yêu cầu hệ thống
- ✅ **Windows 10/11** (64-bit)
- ✅ **Python 3.8+** (Tải tại: https://www.python.org/downloads/)
- ✅ **4GB RAM** trở lên
- ✅ **Kết nối Internet**

### Bước 2: Giải nén package
```
Giải nén file .zip vào thư mục bất kỳ (ví dụ: C:\Xiaozhi)
```

### Bước 3: Chạy INSTALL.bat
```
1. Nhấp đúp vào INSTALL.bat
2. Đợi script cài đặt các dependencies (1-2 phút)
3. Xem thông báo "Cài đặt hoàn tất"
```

### Bước 4: Lấy Xiaozhi Token
```
1. Truy cập: https://xiaozhi.me
2. Đăng nhập (tạo tài khoản nếu chưa có)
3. Vào Profile → Copy JWT token
```

### Bước 5: Khởi động phần mềm
```
1. Nhấp đúp vào START.bat
2. Trình duyệt tự động mở http://localhost:8000
3. Click icon ⚙️ (góc phải trên) → Dán JWT token → Lưu
```

**🎉 HOÀN TẤT! Giờ bạn có thể ra lệnh cho AI!**

---

## 📖 TÀI LIỆU HƯỚNG DẪN

### 🔴 BẮT BUỘC ĐỌC
1. **DISCLAIMER.md** - ⚠️ Điều khoản miễn trách nhiệm (QUAN TRỌNG!)
2. **README.md** - Hướng dẫn chi tiết

### 📘 TÀI LIỆU THAM KHẢO
3. **QUICKSTART.md** - Hướng dẫn nhanh 5 phút
4. **MUSIC_GUIDE.md** - Thư viện nhạc
5. **GEMINI_GUIDE.md** - Google Gemini AI (FREE)
6. **GPT4_GUIDE.md** - OpenAI GPT-4 (PAID)
7. **CHANGELOG.md** - Lịch sử cập nhật

---

## 🎵 THÊM NHẠC VÀO THƯ VIỆN

### Cách thêm nhạc:
```
1. Copy file .mp3/.wav/.flac vào thư mục music_library/
2. Có thể tạo subfolder: Pop/, Rock/, EDM/, v.v.
3. Ra lệnh AI: "Liệt kê nhạc" → Tự động phát bài đầu
```

### Ví dụ cấu trúc:
```
music_library/
├── In Love.mp3
├── Shape of You.mp3
├── Pop/
│   ├── Pop Song 1.mp3
│   └── Pop Song 2.mp3
└── Rock/
    ├── Rock Song 1.mp3
    └── Rock Song 2.mp3
```

**Chi tiết:** Xem `MUSIC_GUIDE.md`

---

## 🤖 CẤU HÌNH AI (TUỲ CHỌN)

### Google Gemini (MIỄN PHÍ - Khuyến nghị)
```
1. Lấy API key: https://aistudio.google.com/apikey
2. Dashboard → ⚙️ → Nhập Gemini API Key → Auto-save
3. Giới hạn: 1500 requests/ngày
```

### OpenAI GPT-4 (TRẢ PHÍ - Chất lượng cao)
```
1. Lấy API key: https://platform.openai.com/api-keys
2. Dashboard → ⚙️ → Nhập OpenAI API Key → Auto-save
3. Chi phí: ~$0.01-0.03/1K tokens
```

**Chi tiết:** Xem `GEMINI_GUIDE.md` và `GPT4_GUIDE.md`

---

## ✅ KIỂM TRA SAU CÀI ĐẶT

Chạy `CHECK.bat` để kiểm tra:
- ✅ Python version
- ✅ Dependencies đã cài đúng
- ✅ Port 8000 có khả dụng
- ✅ Thư viện nhạc đã tạo

---

## 🛠️ TROUBLESHOOTING

### ❌ Lỗi "Python not found"
```
Giải pháp:
1. Cài Python từ https://www.python.org/downloads/
2. Check "Add Python to PATH" khi cài
3. Khởi động lại máy tính
```

### ❌ Server không khởi động
```
Giải pháp:
1. Chạy CHECK.bat để xem lỗi
2. Cài lại dependencies: pip install -r requirements.txt --force-reinstall
3. Kiểm tra port 8000 có bị chiếm không
```

### ❌ Không kết nối Xiaozhi
```
Giải pháp:
1. Kiểm tra JWT token có đúng không
2. Kiểm tra kết nối Internet
3. Xem log trong Dashboard → Tab "Log"
```

### ❌ Nhạc không phát
```
Giải pháp:
1. Kiểm tra file nhạc trong music_library/
2. Đảm bảo Windows Media Player đã cài
3. Thử mở file nhạc thủ công để test
```

**Thêm hỗ trợ:** Xem `README.md` phần Troubleshooting

---

## 📞 HỖ TRỢ

- 🎥 **Kênh YouTube:** https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU
- 📧 **Email:** (Xem trong video YouTube)
- 📝 **Bug Report:** Comment trên video

**LƯU Ý:** Hỗ trợ miễn phí, không cam kết thời gian phản hồi.

---

## ⚠️ ĐIỀU KHOẢN QUAN TRỌNG

### BẮT BUỘC ĐỌC: `DISCLAIMER.md`

**Tóm tắt ngắn gọn:**
- ✅ Miễn phí sử dụng cá nhân, phi thương mại
- ❌ KHÔNG bán lại hoặc sử dụng thương mại
- ❌ KHÔNG xóa credit/logo tác giả
- ⚠️ Người dùng chịu trách nhiệm về việc sử dụng
- ⚠️ Nhà phát triển KHÔNG chịu trách nhiệm về thiệt hại
- ⚠️ Phần mềm cung cấp "AS IS" không bảo hành

**Chi tiết đầy đủ:** Xem file `DISCLAIMER.md`

---

## 🎯 TÍNH NĂNG NỔI BẬT

### 38 Công Cụ Điều Khiển
- **Hệ thống:** Volume, Screenshot, Notification, Brightness, Lock, Shutdown
- **File & Process:** Open app, List/Kill process, Create/Read file
- **Mạng & Web:** Network info, Battery, Search web, Open YouTube/Facebook
- **AI:** Hỏi Gemini, Hỏi GPT-4
- **Nhạc:** List/Play/Search/Stop music với auto-play
- **Tiện ích:** Calculator, Time, Clipboard, Sound, Theme, Wallpaper

### Dashboard Web UI
- 📊 Tất cả 38 công cụ trong 1 trang
- 🎨 Giao diện hiện đại, responsive
- 📋 Log real-time
- ⚙️ Cấu hình dễ dàng

### Thư Viện Nhạc Thông Minh
- 🎵 Auto-play bài đầu tiên
- 🔍 Tìm kiếm fuzzy matching
- 📂 Hỗ trợ subfolder (Pop, Rock, EDM)
- 🎧 Hỗ trợ .mp3, .wav, .flac, .m4a

---

## 📊 PHIÊN BẢN v4.3.0 - DUAL AI EDITION

**Cập nhật mới:**
- 🎉 **2 AI ENGINES:** Gemini (FREE) + GPT-4 (PAID)
- 🤖 Tool `ask_gemini()` - 1500 requests/day
- 🧠 Tool `ask_gpt4()` - Code & reasoning
- 🆕 Auto-save API keys trên Web UI
- ✅ 38 công cụ (36 tools + 2 AI)
- ✅ Music library với auto-play
- ✅ Dashboard UI hiện đại

**Xem thêm:** `CHANGELOG.md`

---

## 🔒 BẢO MẬT

- 🔐 **Dữ liệu local:** Token/API key lưu trên máy bạn
- 🔐 **Không thu thập:** Không gửi thông tin cá nhân về server
- 🔐 **Mã nguồn mở:** Code trong `xiaozhi_final.py` - có thể review
- ⚠️ **Bảo vệ token:** Không chia sẻ file `xiaozhi_endpoints.json`

---

## 📝 LƯU Ý QUAN TRỌNG

### ⚠️ Trước khi sử dụng:
1. ✅ Đọc `DISCLAIMER.md` (bắt buộc)
2. ✅ Backup dữ liệu quan trọng
3. ✅ Hiểu rõ các lệnh nguy hiểm (kill process, shutdown)
4. ✅ Bảo mật JWT token và API keys

### ⚠️ Khi sử dụng:
- Đọc kỹ prompt trước khi xác nhận
- Không chạy lệnh không rõ nguồn gốc
- Giám sát log hoạt động
- Tắt phần mềm khi không dùng

---

## 🎁 PACKAGE NÀY BAO GỒM

- ✅ Phần mềm hoàn chỉnh (không cần cài thêm gì)
- ✅ Tài liệu đầy đủ bằng tiếng Việt
- ✅ Script cài đặt tự động
- ✅ Music library có sẵn cấu trúc
- ✅ Examples và tutorials
- ✅ Điều khoản miễn trách nhiệm rõ ràng
- ✅ Giấy phép MIT (mã nguồn mở)

---

## 📜 GIẤY PHÉP

**MIT License** - Sử dụng miễn phí cho mục đích cá nhân/phi thương mại.

**Chi tiết:** Xem file `LICENSE`

---

## 🙏 LỜI CẢM ƠN

Cảm ơn bạn đã tin tưởng sử dụng **Xiaozhi MCP Control Panel**!

Nếu thấy hữu ích, hãy:
- 👍 Like và Subscribe kênh YouTube miniZ
- 📢 Chia sẻ với bạn bè (phi thương mại)
- 🌟 Đánh giá và góp ý

---

## 📌 QUICK LINKS

- 🎥 **YouTube miniZ:** https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU
- 🌐 **Xiaozhi Official:** https://xiaozhi.me
- 🤖 **Gemini API:** https://aistudio.google.com/apikey
- 🧠 **OpenAI API:** https://platform.openai.com/api-keys

---

**Made with ❤️ by miniZ Team**

*Phiên bản: v4.3.0 Dual AI Edition | Ngày: 16/11/2025*
