# 📦 miniZ MCP v4.3.2 Professional - HƯỚNG DẪN CÀI ĐẶT VÀ SỬ DỤNG

## 🎯 TỔNG QUAN

**miniZ MCP v4.3.2 Professional** là phiên bản cài đặt CHUYÊN NGHIỆP với tính năng:

✅ **Tự động cài đặt tất cả thư viện** - Không cần cài thủ công!  
✅ **Cài xong là dùng ngay** - Thao tác đơn giản, nhanh chóng  
✅ **License key activation** - Kích hoạt trong quá trình cài đặt  
✅ **141 tools đầy đủ** - AI, Music, Web, System control...  
✅ **Dual AI support** - Gemini Flash + GPT-4 (optional)  
✅ **Knowledge Base AI** - Indexing & search với AI  

---

## 📋 YÊU CẦU HỆ THỐNG

### ⚠️ BẮT BUỘC:
- **Windows 10/11** (64-bit)
- **Python 3.11+** đã được cài đặt
  - Download: https://www.python.org/downloads/
  - **QUAN TRỌNG:** Khi cài Python, phải chọn ☑️ **"Add Python to PATH"**
  
### Kiểm tra Python:
```bash
python --version
# Kết quả phải là: Python 3.11.x hoặc cao hơn
```

### Khuyến nghị:
- RAM: 4GB+ (tốt nhất 8GB)
- Disk: 2GB+ free space
- Internet connection (để sử dụng AI)

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT (3 BƯỚC ĐƠN GIẢN)

### Bước 1: Chạy Installer
1. Double-click file: `miniZ_MCP_v4.3.2_Professional_Setup.exe`
2. Nếu Windows hiện "Windows protected your PC", click **"More info"** → **"Run anyway"**

### Bước 2: Làm theo Wizard
1. **License Key:** Nhập key đã được cung cấp (format: XXXX-XXXX-XXXX-XXXX-XXXX)
2. **Install Location:** Để mặc định `C:\Program Files\miniZ_MCP` (khuyến nghị)
3. **Select Components:**
   - ☑️ Tạo Desktop shortcut (khuyến nghị)
   - ☑️ Tạo Start Menu shortcuts
   - ☐ Auto-start cùng Windows (tùy chọn)
4. Click **Install**

### Bước 3: Sau khi cài đặt
Installer sẽ hiện các tùy chọn:

```
☑️ Cài đặt Python dependencies (BẮT BUỘC - chạy lần đầu)
   → Chọn cái này để tự động cài tất cả thư viện!
   → Quá trình mất 2-5 phút
   
☐ Xem hướng dẫn sau cài đặt
☐ Mở thư mục cài đặt
☑️ Khởi động miniZ MCP ngay
```

**✅ Chọn cả 2 option đầu tiên để cài đặt hoàn chỉnh!**

---

## 🎮 CÁCH SỬ DỤNG

### Khởi động lần đầu:
1. Sau khi cài dependencies xong, server sẽ tự động khởi động
2. Console sẽ hiện:
   ```
   ✅ miniZ MCP Server đã khởi động!
   🌐 URL: http://localhost:8000
   🔧 Tổng số tools: 141
   ```

### Khởi động lần sau:
- **Desktop:** Double-click icon "miniZ MCP"
- **Start Menu:** miniZ MCP → miniZ MCP
- **Trực tiếp:** Chạy `START.bat` trong `C:\Program Files\miniZ_MCP\`

### Khởi động ẩn (không hiện console):
- **Start Menu:** miniZ MCP → miniZ MCP (Hidden)
- **Trực tiếp:** Chạy `START_HIDDEN.bat`

---

## ⚙️ CẤU HÌNH API KEYS

Để sử dụng đầy đủ tính năng AI, cần cấu hình API keys:

### 1. Mở file cấu hình:
```
C:\Program Files\miniZ_MCP\xiaozhi_endpoints.json
```

### 2. Thêm API keys:
```json
{
  "GEMINI_API_KEY": "your-gemini-key-here",
  "OPENAI_API_KEY": "your-openai-key-here",    // Optional
  "SERPER_API_KEY": "your-serper-key-here"     // For web search
}
```

### 3. Khởi động lại server

### 🆓 Lấy API Keys miễn phí:

**Gemini AI** (Free - Khuyến nghị):
- URL: https://aistudio.google.com/apikey
- Limit: 1500 requests/day
- Model: gemini-2.0-flash-exp

**Serper API** (Free - Web Search):
- URL: https://serper.dev/api-key
- Limit: 2500 searches/month

**OpenAI** (Optional - Có phí):
- URL: https://platform.openai.com/api-keys
- Models: GPT-4, GPT-3.5-turbo

---

## 🛠️ KHẮC PHỤC SỰ CỐ

### ❌ "Python not found"
**Nguyên nhân:** Python chưa được cài hoặc chưa add vào PATH

**Giải pháp:**
1. Cài Python 3.11+ từ: https://www.python.org/downloads/
2. **QUAN TRỌNG:** Chọn ☑️ "Add Python to PATH" khi cài
3. Khởi động lại máy tính
4. Kiểm tra: `python --version` trong CMD

### ❌ "Port 8000 already in use"
**Nguyên nhân:** Có chương trình khác đang dùng port 8000

**Giải pháp:**
```bash
taskkill /F /IM python.exe
# Sau đó khởi động lại miniZ MCP
```

### ❌ "Module not found" / Import errors
**Nguyên nhân:** Dependencies chưa được cài đặt

**Giải pháp:**
1. Chạy file: `C:\Program Files\miniZ_MCP\AUTO_INSTALL_DEPENDENCIES.bat`
2. Đợi 2-5 phút để cài đặt
3. Khởi động lại server

### ❌ Server không khởi động
**Kiểm tra:**
1. Chạy: `C:\Program Files\miniZ_MCP\CHECK.bat`
2. Xem logs trong thư mục: `C:\Program Files\miniZ_MCP\logs\`
3. Kiểm tra quyền truy cập thư mục

---

## 📚 TÀI LIỆU CHI TIẾT

Sau khi cài đặt, xem các file hướng dẫn trong thư mục cài đặt:

| File | Nội dung |
|------|----------|
| `QUICKSTART.md` | Hướng dẫn nhanh cho người mới |
| `GEMINI_GUIDE.md` | Cấu hình Gemini AI chi tiết |
| `GPT4_GUIDE.md` | Cấu hình GPT-4/ChatGPT |
| `MUSIC_GUIDE.md` | Sử dụng Music Player với VLC |
| `README.md` | Tài liệu đầy đủ 141 tools |
| `CHANGELOG.md` | Lịch sử cập nhật phiên bản |

---

## 🎯 TÍNH NĂNG CHÍNH

### 🤖 AI Integration
- **Gemini Flash 2.0** - Summarization & Knowledge Base
- **GPT-4** - Advanced reasoning (optional)
- **Knowledge Base AI** - Auto-indexing documents với TF-IDF search
- **Context-aware responses** - LLM nhận context từ Knowledge Base

### 🎵 Music Player
- **VLC integration** - Play local music files
- **Playlist management** - Next/previous/stop
- **Search by keyword** - Tìm và phát nhạc tự động
- **Music library** - Organize by genre

### 🌐 Web & Search
- **Real-time web search** - Google search via Serper API
- **YouTube search** - Find videos and playlists
- **Website content fetch** - Extract text from URLs

### 💻 System Control
- **File operations** - Read, write, search files
- **Screenshot** - Capture screen và save
- **Clipboard** - Copy/paste text
- **Power control** - Shutdown, restart, sleep
- **Volume control** - Điều chỉnh âm lượng hệ thống

### 📊 Data & Memory
- **Auto-save conversations** - Lưu lịch sử chat
- **Task memory** - Ghi nhớ tasks và progress
- **User profiles** - Lưu thông tin người dùng
- **RAG cache** - Cache cho Knowledge Base

---

## 📞 HỖ TRỢ

### Liên hệ:
- 🌐 Website: https://miniz-mcp.com
- 📧 Email: support@miniz-mcp.com
- 📱 Telegram: @miniz_mcp_support
- 💬 Discord: discord.gg/miniz-mcp

### Báo lỗi:
- GitHub Issues: https://github.com/miniz-mcp/issues
- Email: bugs@miniz-mcp.com

---

## 📋 CHECKLIST SAU CÀI ĐẶT

✅ Python 3.11+ đã cài và có trong PATH  
✅ Dependencies đã được cài đặt (chạy AUTO_INSTALL_DEPENDENCIES.bat)  
✅ Server khởi động thành công (thấy "Server running on port 8000")  
✅ API keys đã được cấu hình (Gemini, Serper)  
✅ Xiaozhi App đã kết nối thành công (http://localhost:8000)  
✅ Test 1-2 tools để đảm bảo hoạt động (vd: file_read, web_search)  

---

## 🎊 CHÚC BẠN SỬ DỤNG miniZ MCP VUI VẺ!

**Lưu ý quan trọng:**
- License key chỉ sử dụng cho 1 máy tính
- Không chia sẻ license key với người khác
- Backup conversations và config thường xuyên
- Cập nhật phiên bản mới khi có thông báo

---

© 2024-2025 miniZ MCP Team. All rights reserved.  
Licensed under miniZ MCP Professional License v4.3.2
