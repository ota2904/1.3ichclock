# Changelog

All notable changes to Xiaozhi MCP Control Panel will be documented in this file.

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

**Repository:** https://github.com/nguyenconghuy2904-source/miniz_pc_tool2
