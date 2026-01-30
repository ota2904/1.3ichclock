# Changelog

All notable changes to Xiaozhi MCP Control Panel will be documented in this file.

## [4.3.0] - 2025-11-06 (Dual AI Edition)

### 🎉 Dual AI Integration - Gemini + GPT-4

#### Added
- **Google Gemini AI Integration** (MIỄN PHÍ)
  - New tool: `ask_gemini()` - Hỏi đáp với Gemini AI
  - Models: models/gemini-2.5-pro (default), gemini-2.5-flash
  - API key configuration trong `xiaozhi_endpoints.json`
  - Auto-save API key trên Web UI
  - 1500 requests/day miễn phí

- **OpenAI GPT-4 Integration** (TRẢ PHÍ)
  - New tool: `ask_gpt4()` - Hỏi đáp với GPT-4
  - Models: gpt-4o (default), gpt-4-turbo, gpt-3.5-turbo
  - Auto-save OpenAI API key
  - Token usage tracking
  - $5 free trial credit
  - Comprehensive error handling

#### Dependencies
- Added `google-generativeai==0.8.3` for Gemini
- Added `openai==1.54.0` for GPT-4

#### Documentation
- New file: `GEMINI_GUIDE.md` - Complete guide for Gemini AI usage (400+ lines)
- New file: `GPT4_GUIDE.md` - Complete guide for GPT-4 usage
- New file: `HUONG_DAN_THONG_TIN_MOI.md` - Real-time info guide
- New file: `DUAL_AI_SUMMARY.txt` - Dual AI summary
- Updated `README.md` with Dual AI section
- Updated tool descriptions to optimize AI selection
- Examples and troubleshooting guide

#### Use Cases
- Hỏi đáp thông tin
- Phân tích code
- Viết nội dung, email
- Dịch thuật
- Giải toán
- Brainstorming

#### Technical
- Async implementation với `run_in_executor()`
- Non-blocking API calls
- Quota tracking support (1500 requests/day free)
- Model selection support
- Rate limit and error handling

---

## [4.2.0] - 2025-11-03

### ✨ Audio Control Enhancement

#### Added
- **4 New Audio Control Commands**
  - `mute_volume` - Tắt tiếng hệ thống 🔇
  - `unmute_volume` - Bật lại tiếng 🔊
  - `volume_up` - Tăng âm lượng (tùy chỉnh bước) 🔊
  - `volume_down` - Giảm âm lượng (tùy chỉnh bước) 🔉

#### Fixed
- **Python 3.13 Compatibility**
  - Replaced pycaw audio library with PowerShell SendKeys method
  - Fixed `_compointer_base` error from comtypes incompatibility
  - All audio controls now work on Python 3.13+

#### Technical
- PowerShell WScript.Shell SendKeys for volume control
- Cross-version compatibility (Python 3.8 - 3.13)
- No external audio library dependencies

---

## [4.1.0] - 2025-11-03

### ✨ UI/UX Improvements & Playlist Manager

#### Added
- **YouTube Playlist Manager**
  - Multi-playlist support with fuzzy search
  - Add/remove playlists via UI
  - Open playlists with voice commands
  - Name-based quick access
  - Stored in browser localStorage

#### Changed
- **Dashboard Optimization**
  - Moved Log panel to bottom of Dashboard
  - Removed redundant YouTube playlist banner
  - Removed Log from sidebar menu
  - Improved visibility and workflow

#### Fixed
- Volume and brightness controls functionality
- Missing `/api/tool/set_volume` endpoint
- Installed `screen-brightness-control` package

---

## [4.0.0] - 2025-11-03

### 🎉 Production Release

#### Added
- **miniZ Branding**
  - Compact corner footer with logo
  - YouTube channel link
  - Professional branding throughout UI

#### Changed
- **Documentation Cleanup**
  - Removed all GitHub references from packaged docs
  - Replaced with miniZ YouTube links
  - Customer-ready documentation

#### Technical
- PyInstaller 6.16.0 for standalone .exe
- 41.35 MB executable with all dependencies
- No Python installation required

---

## [1.0.0] - 2025-11-03

### 🎉 Initial Release

#### ✨ Added
- **30 Tools Implementation**
  - 7 System tools (volume, screenshot, notification, resources, brightness, lock, shutdown)
  - 7 File & Process tools (open app, list/kill process, create/read/list files, disk usage)
  - 3 Network tools (network info, battery, web search)
  - 13 Utility tools (calculator, time, clipboard, sound, desktop, undo, theme, wallpaper, paste, enter, find)

- **Web Dashboard**
  - Sidebar navigation (Dashboard, Tools, Config, Log)
  - 30 color-coded action cards with icons
  - 4-tab tool organization
  - Real-time activity log
  - Purple gradient theme

- **MCP Integration**
  - WebSocket client with auto-retry
  - JWT token authentication
  - Multi-device support (3 devices)
  - MCP Protocol 2024-11-05 compliance

- **Single-File Deployment**
  - Embedded HTML/CSS/JavaScript
  - No build process required
  - 1200+ lines of clean code

#### 🛠️ Technical Stack
- FastAPI 0.104.1
- Python 3.13
- psutil, requests, websockets
- pyautogui, pyperclip

#### 📝 Documentation
- Complete README.md with installation guide
- MIT License
- requirements.txt with exact versions
- Windows batch/PowerShell launchers

---

## [Planned Features]

### 🚀 Version 1.1.0 (Coming Soon)
- [ ] Add 20+ more tools from xiaozhi-MCPTools reference
- [ ] WeChat integration (send messages, files)
- [ ] PPT control (next/prev/start/stop)
- [ ] Music player control (LuoXue integration)
- [ ] Document automation (Word, Excel)

### 🔮 Version 2.0.0 (Future)
- [ ] Plugin system for custom tools
- [ ] Dashboard authentication
- [ ] Multi-language support (EN/VI/CN)
- [ ] Docker deployment
- [ ] Mobile app companion
- [ ] Voice command integration

---

**Phát triển bởi miniZ** | [YouTube Channel](https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU)
