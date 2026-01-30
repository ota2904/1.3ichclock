#  miniZ MCP - Build Package

##  Nội dung Package

Thư mục này chứa tất cả file cần thiết để build miniZ MCP:

### File chính:
- `xiaozhi_final.py` - File Python chính (mới nhất với Gemini AI KB search)
- `build_to_dist.py` - Script build tự động
- `requirements.txt` - Dependencies
- `logo.ico`, `logo.png` - Icons
- `xiaozhi_endpoints.json` - Cấu hình endpoints

### Modules hỗ trợ:
- `config_manager.py` - Quản lý cấu hình
- `license_manager.py` - Quản lý license
- `tray_app.py` - System tray app
- `vlc_mcp_server.py` - VLC control
- `rag_system.py` - RAG system
- `vector_search.py` - Vector search
- `startup_manager.py` - Startup manager

### Thư mục:
- `fw_images/` - Wallpaper images (30 files)

##  Cách Build

### 1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
pip install pyinstaller
```

### 2. Build:
```bash
BUILD.bat
```
hoặc:
```bash
python build_to_dist.py
```

### 3. Kết quả:
- File EXE: `dist\miniZ_MCP.exe`
- Kích thước: ~80-85 MB
- Chạy standalone, không cần Python

##  Tính năng mới nhất (Updated: 2026-01-28)

-  Gemini 2.0 Flash model
-  KB Search với Gemini AI - Trả lời trực tiếp từ tài liệu
-  Gold price analysis tool
-  143 AI tools
-  Dual AI support (Gemini + GPT-4)

##  Build Info

- Python: 3.14+
- Build tool: PyInstaller 6.17+
- Platform: Windows 11
- Build time: ~2-3 phút

##  Run sau khi build

```bash
cd dist
miniZ_MCP.exe
```

Server sẽ chạy tại: `http://localhost:8000`
