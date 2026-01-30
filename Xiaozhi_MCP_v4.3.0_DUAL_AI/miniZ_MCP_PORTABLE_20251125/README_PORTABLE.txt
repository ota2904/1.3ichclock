================================================================================
                        🌳 miniZ MCP v4.3.0 PORTABLE
                    HƯỚNG DẪN CÀI ĐẶT VÀ SỬ DỤNG ĐẦY ĐỦ
================================================================================

📅 Phiên bản: v4.3.0 PORTABLE - 25/11/2025
🎯 Mục đích: Điều khiển máy tính bằng AI (Google Gemini + OpenAI GPT-4)
📦 Tính năng: 30+ công cụ điều khiển Windows qua giọng nói và text

================================================================================
                        📋 MỤC LỤC
================================================================================

1. GIỚI THIỆU TỔNG QUAN
2. YÊU CẦU HỆ THỐNG
3. CÀI ĐẶT NHANH (3 BƯỚC)
4. CẤU HÌNH API KEYS
5. TÍNH NĂNG CHI TIẾT
6. SỬ DỤNG CƠ BẢN
7. XỬ LÝ SỰ CỐ
8. CÂU HỎI THƯỜNG GẶP
9. LIÊN HỆ HỖ TRỢ

================================================================================
                        1. GIỚI THIỆU TỔNG QUAN
================================================================================

🌟 miniZ MCP là gì?

miniZ MCP (Model Context Protocol) là phần mềm điều khiển máy tính Windows 
bằng trí tuệ nhân tạo. Bạn có thể ra lệnh bằng tiếng Việt hoặc tiếng Anh 
để thực hiện hơn 30 tác vụ khác nhau.

✨ ĐIỂM NỔI BẬT:
    ✓ Dual AI System: Google Gemini (miễn phí) + OpenAI GPT-4 (trả phí)
    ✓ 30+ công cụ: Volume, Screenshot, Browser, Music, YouTube, v.v.
    ✓ Web UI đẹp mắt: Giao diện Sidebar hiện đại, dễ sử dụng
    ✓ VLC Integration: Phát nhạc local + playlist + next/previous
    ✓ Browser Automation: Selenium điều khiển Chrome/Edge
    ✓ YouTube Playlist: Quản lý playlist YouTube qua Web UI
    ✓ Portable: Không cần install, chạy trực tiếp từ thư mục

🎨 KIẾN TRÚC:
    • Single-file Python: xiaozhi_final.py (5600+ dòng)
    • FastAPI + WebSocket: Real-time communication
    • MCP Protocol: Multi-device support
    • VLC Player: python-vlc 3.0.18121
    • Selenium 4.15.2: Browser automation

================================================================================
                        2. YÊU CẦU HỆ THỐNG
================================================================================

📌 BẮT BUỘC:

    ✅ HỆ ĐIỀU HÀNH:
        • Windows 10 (64-bit) hoặc Windows 11
        • Quyền Administrator (để cài Python packages)

    ✅ PYTHON:
        • Python 3.8 trở lên (KhuyếnGoogle nghị: Python 3.11-3.13)
        • Tải từ: https://www.python.org/downloads/
        • ⚠️ QUAN TRỌNG: Tick "Add Python to PATH" khi cài đặt

    ✅ INTERNET:
        • Kết nối Internet ổn định
        • Tốc độ tối thiểu: 5 Mbps
        • Để sử dụng AI và YouTube features

📌 KHUYẾN NGHỊ (Không bắt buộc):

    ✅ VLC MEDIA PLAYER:
        • Tải từ: https://www.videolan.org/vlc/
        • Cần để sử dụng tính năng phát nhạc local

    ✅ GOOGLE CHROME hoặc EDGE:
        • Để sử dụng browser automation
        • Selenium sẽ tự động tải ChromeDriver

    ✅ PHẦN CỨNG:
        • RAM: Tối thiểu 4GB (Khuyến nghị 8GB+)
        • CPU: Intel Core i3 hoặc tương đương
        • Ổ cứng: 500MB trống

================================================================================
                        3. CÀI ĐẶT NHANH (3 BƯỚC)
================================================================================

🚀 BƯỚC 1: GIẢI NÉN PACKAGE

    1. Giải nén file miniZ_MCP_PORTABLE_YYYYMMDD.zip
    2. Chọn vị trí: Ví dụ: C:\miniZ_MCP\ hoặc D:\Tools\miniZ\
    3. ⚠️ TRÁNH: Đường dẫn có dấu tiếng Việt hoặc ký tự đặc biệt

📦 CẤU TRÚC THƯ MỤC SAU KHI GIẢI NÉN:

    miniZ_MCP_PORTABLE_20251125/
    ├── xiaozhi_final.py           ← File chính (5600+ dòng)
    ├── requirements.txt            ← Danh sách Python packages
    ├── logo.png                    ← Logo miniZ MCP
    ├── xiaozhi_endpoints.json      ← Cấu hình API keys (CẦN CHỈNH SỬA!)
    ├── youtube_playlists.json      ← Playlist YouTube
    ├── DISCLAIMER.txt              ← Chính sách miễn trừ trách nhiệm
    ├── README_PORTABLE.txt         ← File này (hướng dẫn)
    ├── INSTALL.bat                 ← Script cài đặt (click để chạy)
    ├── START.bat                   ← Script khởi động (click để chạy)
    └── music_library/              ← Thư viện nhạc local
        ├── Pop/
        ├── Rock/
        └── Classical/

🚀 BƯỚC 2: CÀI ĐẶT DEPENDENCIES

    CÁCH 1: Sử dụng INSTALL.bat (Khuyến nghị)
        1. Double-click vào file INSTALL.bat
        2. Chờ tự động cài đặt (3-5 phút)
        3. Xem output để đảm bảo không có lỗi

    CÁCH 2: Cài đặt thủ công (Nâng cao)
        1. Mở Command Prompt (CMD)
        2. cd đến thư mục miniZ_MCP
        3. Chạy: python -m pip install -r requirements.txt

    📦 PACKAGES SẼ ĐƯỢC CÀI:
        • fastapi==0.104.1          (Web framework)
        • uvicorn[standard]==0.24.0 (ASGI server)
        • websockets==12.0          (WebSocket support)
        • psutil==5.9.6             (System info)
        • pyautogui==0.9.54         (Screenshot, keyboard)
        • pycaw                     (Volume control)
        • comtypes                  (Windows COM)
        • python-vlc==3.0.18121     (VLC music player)
        • selenium==4.15.2          (Browser automation)
        • webdriver-manager==4.0.1  (Auto ChromeDriver)
        • youtube-search-python==1.6.6 (YouTube search)

🚀 BƯỚC 3: CẤU HÌNH API KEYS

    1. Mở file: xiaozhi_endpoints.json bằng Notepad
    2. Điền API keys của bạn (xem mục 4 bên dưới)
    3. Save file và đóng lại

✅ HOÀN TẤT! Bây giờ có thể khởi động bằng START.bat

================================================================================
                        4. CẤU HÌNH API KEYS
================================================================================

⚠️ QUAN TRỌNG: Phần mềm CẦN API keys để hoạt động!

📝 FILE CẤU HÌNH: xiaozhi_endpoints.json

Mở file này và điền thông tin:

```json
[
  {
    "name": "Google Gemini Free",
    "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
    "api_key": "YOUR_GEMINI_API_KEY_HERE",
    "model": "gemini-2.0-flash-exp",
    "is_default": true
  },
  {
    "name": "OpenAI GPT-4",
    "endpoint": "https://api.openai.com/v1/chat/completions",
    "api_key": "YOUR_OPENAI_API_KEY_HERE",
    "model": "gpt-4",
    "is_default": false
  }
]
```

🔑 CÁCH LẤY API KEYS:

📍 GOOGLE GEMINI (MIỄN PHÍ):
    1. Truy cập: https://aistudio.google.com/app/apikey
    2. Đăng nhập Google Account
    3. Click "Create API Key"
    4. Copy API key và paste vào "api_key" của Gemini
    5. ✅ Miễn phí, giới hạn 60 requests/phút

📍 OPENAI GPT-4 (TRẢ PHÍ - OPTIONAL):
    1. Truy cập: https://platform.openai.com/api-keys
    2. Đăng nhập OpenAI Account
    3. Click "Create new secret key"
    4. Copy API key và paste vào "api_key" của OpenAI
    5. ⚠️ Trả phí: ~$0.03/1K tokens (input), ~$0.06/1K tokens (output)

💡 KHUYẾN NGHỊ:
    • Dùng Google Gemini làm mặc định (is_default: true)
    • OpenAI GPT-4 chỉ dùng khi cần độ chính xác cao
    • Có thể xóa endpoint OpenAI nếu không dùng

⚠️ BẢO MẬT API KEYS:
    ✗ KHÔNG chia sẻ API keys cho người khác
    ✗ KHÔNG commit file này lên GitHub
    ✗ KHÔNG đăng API keys lên mạng xã hội

================================================================================
                        5. TÍNH NĂNG CHI TIẾT
================================================================================

🎯 30+ CÔNG CỤ ĐIỀU KHIỂN WINDOWS:

📢 ÂM LƯỢNG (6 tools):
    • set_volume(level)       : Đặt âm lượng cụ thể (0-100)
    • get_volume()            : Kiểm tra âm lượng hiện tại
    • mute_volume()           : Tắt tiếng
    • unmute_volume()         : Bật lại tiếng
    • volume_up(steps=5)      : Tăng âm lượng
    • volume_down(steps=5)    : Giảm âm lượng

📸 CHỤP MÀN HÌNH:
    • take_screenshot(filename): Chụp toàn bộ màn hình, lưu vào Downloads

🔔 THÔNG BÁO:
    • show_notification(title, message): Hiển thị Windows notification

💻 HỆ THỐNG:
    • get_system_resources()  : CPU, RAM, Disk usage
    • lock_computer()         : Khóa màn hình
    • shutdown_schedule(action, delay): Tắt/restart máy

🌐 ĐIỀU KHIỂN BROWSER (10 tools - Selenium):
    • open_browser(url)       : Mở trình duyệt với URL
    • close_browser()         : Đóng trình duyệt
    • navigate_to(url)        : Điều hướng đến URL
    • click_element(selector) : Click phần tử (CSS selector)
    • fill_input(selector, text): Điền text vào input
    • take_browser_screenshot(filename): Chụp màn hình browser
    • scroll_page(direction, amount): Cuộn trang (up/down)
    • get_page_title()        : Lấy tiêu đề trang
    • get_current_url()       : Lấy URL hiện tại
    • execute_js(script)      : Chạy JavaScript

🎵 NHẠC LOCAL (VLC Integration):
    • list_music()            : Liệt kê nhạc trong music_library/
    • play_music(path)        : Phát nhạc local
    • pause_music()           : Tạm dừng
    • stop_music()            : Dừng hẳn
    • next_track()            : Bài tiếp theo (trong playlist)
    • previous_track()        : Bài trước

📺 YOUTUBE:
    • search_youtube_video(title): Tìm video YouTube
    • open_youtube_playlist(name): Mở playlist đã lưu

🖥️ ỨNG DỤNG:
    • open_application(name)  : Mở ứng dụng (50+ apps hỗ trợ)
    • list_available_apps()   : Liệt kê apps có thể mở

⌨️ THAO TÁC:
    • type_text(text)         : Gõ text
    • press_hotkey(key1, key2): Nhấn phím tắt
    • press_enter()           : Nhấn Enter
    • paste_content(content)  : Paste text

================================================================================
                        6. SỬ DỤNG CƠ BẢN
================================================================================

🚀 KHỞI ĐỘNG PHẦN MỀM:

    CÁCH 1: Double-click START.bat
        • File batch tự động khởi động
        • Browser tự động mở sau 2 giây

    CÁCH 2: Thủ công
        1. Mở Command Prompt
        2. cd đến thư mục miniZ_MCP
        3. Chạy: python xiaozhi_final.py
        4. Mở browser: http://localhost:8000

✅ KHI KHỞI ĐỘNG THÀNH CÔNG:
    • Terminal hiển thị: "miniZ MCP - SIDEBAR UI"
    • Browser tự động mở Web UI
    • Logo miniZ MCP hiển thị ở sidebar
    • WebSocket kết nối: "Connected! (Thiết bị 3)"

🎨 GIAO DIỆN WEB UI:

    SIDEBAR (Bên trái):
        📊 Dashboard : Trang chủ, thông tin hệ thống
        🛠️ Công Cụ  : Danh sách 30 tools, test thủ công
        🎵 Playlist  : Quản lý YouTube playlists

    MAIN AREA (Bên phải):
        • Chat box để giao tiếp với AI
        • System info: CPU, RAM, Disk
        • Output của các tools

💬 CHAT VỚI AI:

    Ví dụ lệnh tiếng Việt:
        "Chỉnh âm lượng 50"
        "Chụp màn hình"
        "Mở Chrome"
        "Tìm video YouTube: Sơn Tùng MTP"
        "Tắt tiếng"
        "Khóa máy"

    Ví dụ lệnh tiếng Anh:
        "Set volume to 80"
        "Take a screenshot"
        "Open browser google.com"
        "Mute volume"
        "Show system resources"

🎵 PHÁT NHẠC LOCAL:

    1. Copy file MP3 vào thư mục: music_library/Pop/
    2. Chat: "Phát nhạc Pop"
    3. AI sẽ liệt kê nhạc và cho bạn chọn
    4. Hoặc: "Phát bài [tên bài]"

    ĐIỀU KHIỂN:
        "Dừng nhạc"
        "Tạm dừng"
        "Bài tiếp theo"
        "Bài trước"

📺 YOUTUBE PLAYLIST:

    1. Click tab "🎵 Playlist YouTube"
    2. Nhập tên playlist: "Nhạc Việt Hay"
    3. Nhập URL: https://youtube.com/playlist?list=...
    4. Click "Thêm Playlist"
    5. Chat: "Mở playlist Nhạc Việt Hay"

================================================================================
                        7. XỬ LÝ SỰ CỐ
================================================================================

❌ LỖI: "Python không được tìm thấy"

    NGUYÊN NHÂN: Python chưa được cài hoặc không có trong PATH
    GIẢI PHÁP:
        1. Cài Python từ python.org
        2. Tick "Add Python to PATH" khi cài
        3. Khởi động lại Command Prompt

❌ LỖI: "Module not found"

    NGUYÊN NHÂN: Thiếu Python packages
    GIẢI PHÁP:
        1. Chạy lại INSTALL.bat
        2. Hoặc: pip install -r requirements.txt
        3. Kiểm tra: pip list

❌ LỖI: "Port 8000 already in use"

    NGUYÊN NHÂN: Cổng 8000 đang được dùng
    GIẢI PHÁP:
        1. Đóng process đang dùng port 8000
        2. Hoặc sửa port trong xiaozhi_final.py (dòng cuối)
        3. Hoặc: netstat -ano | findstr :8000 → taskkill /PID <PID> /F

❌ LỖI: "API key invalid"

    NGUYÊN NHÂN: API key sai hoặc hết hạn
    GIẢI PHÁP:
        1. Kiểm tra xiaozhi_endpoints.json
        2. Generate API key mới từ Google/OpenAI
        3. Copy-paste lại chính xác (không có dấu cách thừa)

❌ LỖI: VLC không phát được nhạc

    NGUYÊN NHÂN: VLC Media Player chưa được cài
    GIẢI PHÁP:
        1. Tải VLC từ videolan.org
        2. Cài VLC (mặc định C:\Program Files\VideoLAN\VLC\)
        3. Restart phần mềm miniZ MCP

❌ LỖI: Browser automation không hoạt động

    NGUYÊN NHÂN: Thiếu Chrome/Edge hoặc ChromeDriver lỗi
    GIẢI PHÁP:
        1. Cài Google Chrome (hoặc Edge)
        2. Chạy lệnh: pip install --upgrade selenium webdriver-manager
        3. Restart phần mềm

❌ LỖI: Screenshot lỗi "Access denied"

    NGUYÊN NHÂN: Thiếu quyền truy cập thư mục Downloads
    GIẢI PHÁP:
        1. Kiểm tra quyền thư mục C:\Users\[User]\Downloads
        2. Chạy CMD as Administrator
        3. Thử lại

================================================================================
                        8. CÂU HỎI THƯỜNG GẶP
================================================================================

❓ Phần mềm có miễn phí không?

    ✓ Google Gemini API: MIỄN PHÍ (giới hạn 60 requests/phút)
    ✗ OpenAI GPT-4 API: TRẢ PHÍ (~$0.03-0.06/1K tokens)
    ✓ Phần mềm miniZ MCP: Tùy license (liên hệ nhà phát triển)

❓ Có cần Internet không?

    ✓ CẦN Internet cho: AI chat, YouTube features
    ✓ KHÔNG CẦN cho: Volume control, screenshot, lock computer, local music

❓ Có chạy trên Mac/Linux không?

    ✗ KHÔNG. Chỉ hỗ trợ Windows 10/11 (64-bit)

❓ Có bị virus không?

    ✓ KHÔNG. Phần mềm sạch, đã kiểm tra kỹ (xem DISCLAIMER.txt)
    ✓ Có thể scan bằng VirusTotal để yên tâm

❓ API keys có bị lộ không?

    ✓ KHÔNG. API keys lưu local trên máy bạn
    ✓ Không gửi về server bên ngoài
    ⚠️ Tuy nhiên hãy BẢO MẬT file xiaozhi_endpoints.json

❓ Làm sao để cập nhật phần mềm?

    1. Tải phiên bản mới
    2. Backup file xiaozhi_endpoints.json và youtube_playlists.json
    3. Giải nén phiên bản mới
    4. Copy 2 file backup vào thư mục mới
    5. Chạy lại INSTALL.bat

❓ Có thể tùy chỉnh giao diện không?

    ✓ CÓ. Có thể sửa CSS trong xiaozhi_final.py
    ⚠️ Cần kiến thức HTML/CSS
    ⚠️ Backup file gốc trước khi sửa

❓ Có hỗ trợ tiếng Việt không?

    ✓ CÓ. Hỗ trợ đầy đủ tiếng Việt (có dấu)
    ✓ AI hiểu cả lệnh tiếng Việt và tiếng Anh

❓ Làm sao thêm nhạc vào thư viện?

    1. Copy file MP3 vào: music_library/Pop/ (hoặc Rock, Classical)
    2. Có thể tạo thêm thư mục con
    3. Chat: "Liệt kê nhạc Pop"
    4. Chat: "Phát bài [tên file]"

❓ Có giới hạn số lượng playlist YouTube không?

    ✓ KHÔNG giới hạn
    ✓ Có thể thêm bao nhiêu playlist tùy thích

❓ Có thể chạy nhiều instance không?

    ✗ KHÔNG khuyến nghị (vì port 8000 bị trùng)
    ✓ Có thể sửa port nếu muốn chạy nhiều instance

================================================================================
                        9. LIÊN HỆ HỖ TRỢ
================================================================================

📧 HỖ TRỢ KỸ THUẬT:
    • Chỉ hỗ trợ cho khách hàng đã mua phần mềm
    • Email: (Sẽ được cung cấp sau khi mua)
    • Thời gian: 9h-18h, Thứ 2-6 (trừ ngày lễ)

📝 BÁO LỖI:
    Khi báo lỗi, vui lòng cung cấp:
        • Phiên bản Windows (Win 10/11)
        • Phiên bản Python (python --version)
        • Nội dung lỗi (copy từ terminal)
        • Các bước tái hiện lỗi

💡 CỘNG ĐỒNG:
    • (Sẽ có group Telegram/Discord sau này)

🔄 CẬP NHẬT:
    • Kiểm tra phiên bản mới: (Liên hệ qua email)
    • Miễn phí trong 6 tháng đầu
    • Sau đó: phí gia hạn 30% giá gốc

================================================================================
                        📌 CHECKLIST TRƯỚC KHI GIAO KHÁCH
================================================================================

☑ ĐIỀU KIỆN BẮT BUỘC:
    □ Đã đọc và đồng ý DISCLAIMER.txt
    □ Đã cài Python 3.8+ (tick "Add to PATH")
    □ Đã chạy INSTALL.bat thành công
    □ Đã điền API keys vào xiaozhi_endpoints.json
    □ Đã test chạy START.bat thành công
    □ Web UI mở được tại http://localhost:8000
    □ Chat với AI hoạt động bình thường

☑ KHUYẾN NGHỊ:
    □ Đã cài VLC Media Player (cho tính năng nhạc)
    □ Đã cài Google Chrome (cho browser automation)
    □ Đã backup file xiaozhi_endpoints.json
    □ Đã test 5-10 lệnh cơ bản

☑ BẢO MẬT:
    □ KHÔNG chia sẻ API keys
    □ KHÔNG public file xiaozhi_endpoints.json
    □ Đã đọc phần bảo mật trong DISCLAIMER.txt

================================================================================
                        🎉 CHÚC BẠN SỬ DỤNG VUI VẺ!
================================================================================

Cảm ơn bạn đã tin tưởng và sử dụng miniZ MCP v4.3.0!

Nếu hài lòng với sản phẩm, hãy giới thiệu cho bạn bè. ❤️

🌳 miniZ MCP - Điều khiển máy tính thông minh
📅 Version: 4.3.0 PORTABLE - 25/11/2025

================================================================================
                        © 2025 miniZ MCP. All Rights Reserved.
================================================================================
