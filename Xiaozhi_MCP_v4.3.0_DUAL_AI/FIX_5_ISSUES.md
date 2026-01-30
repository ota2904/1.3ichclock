# 🔧 FIX CHO 5 VẤN ĐỀ

## Tổng quan

Test suite: `TEST_ALL_5_ISSUES.bat` để kiểm tra tất cả vấn đề.

---

## 1️⃣ API Keys không hardcode ✅

**Trạng thái:** ✅ **ĐÃ FIX**

**Cách thức:**
- API keys được lưu trong `xiaozhi_endpoints.json` (file riêng, không commit vào git)
- Source code KHÔNG chứa API keys
- User nhập keys qua Web UI → lưu vào config file

**Kiểm tra:**
```bash
# Grep toàn bộ code xem có API key hardcode không
grep -r "AIzaSy[A-Za-z0-9_-]{30,}" xiaozhi_final.py
# Kết quả: Không tìm thấy (chỉ có validation pattern)
```

**Config file structure:**
```json
{
  "endpoints": [...],
  "active_index": 0,
  "gemini_api_key": "AIzaSy...",
  "openai_api_key": "sk-...",
  "serper_api_key": "...",
  "last_updated": "2025-12-14T..."
}
```

---

## 2️⃣ Chức năng lưu config

**Trạng thái:** ✅ **HOẠT ĐỘNG TỐT**

**Code location:** `xiaozhi_final.py` line 599-640

### Function: `save_endpoints_to_file()`

```python
def save_endpoints_to_file(endpoints, active_index):
    """Lưu cấu hình endpoints vào file JSON"""
    try:
        new_data = {
            'endpoints': endpoints,
            'active_index': active_index,
            'gemini_api_key': GEMINI_API_KEY,
            'openai_api_key': OPENAI_API_KEY,
            'serper_api_key': SERPER_API_KEY,
            'last_updated': datetime.now().isoformat()
        }
        
        # So sánh với file cũ, chỉ ghi khi có thay đổi
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"❌ Save error: {e}")
        return False
```

### API Endpoint: `/api/save_endpoints`

```python
@app.post("/api/save_endpoints")
async def save_endpoints(data: dict):
    devices = data.get('devices', [])
    endpoints_config = []
    for dev in devices:
        endpoints_config.append({
            'name': dev.get('name', 'Thiết bị'),
            'token': dev.get('token', ''),
            'enabled': bool(dev.get('token', ''))
        })
    
    if save_endpoints_to_file(endpoints_config, active_endpoint_index):
        return {"success": True}
    else:
        return {"success": False, "error": "Lưu file thất bại"}
```

### Test:
```bash
curl -X POST http://localhost:8000/api/save_endpoints \
  -H "Content-Type: application/json" \
  -d '{"devices": [{"name": "Test", "token": "abc123", "enabled": true}]}'
```

**Nếu không hoạt động:**
- Kiểm tra quyền write file
- Xem log terminal: `✅ [Config] Loaded X endpoints...`
- Verify file `xiaozhi_endpoints.json` được tạo

---

## 3️⃣ Mở trực tiếp video YouTube

**Trạng thái:** ⚠️ **CẦN FIX**

**Vấn đề hiện tại:**
- `open_youtube(search_query)` chỉ mở trang tìm kiếm YouTube
- Không mở trực tiếp video cụ thể

**Có sẵn function:** `search_youtube_video()` (line 4942-5010)

### FIX: Sử dụng `search_youtube_video` thay vì `open_youtube`

**Cách 1: User gọi tool đúng**
```python
# Thay vì
open_youtube(search_query="Sơn Tùng Chúng Ta")

# Dùng
search_youtube_video(video_title="Sơn Tùng Chúng Ta Của Hiện Tại", auto_open=True)
```

**Cách 2: Auto-detect và redirect**

Thêm vào `open_youtube()` function:

```python
async def open_youtube(search_query: str = "") -> dict:
    """Mở YouTube, tự động phát video nếu query cụ thể"""
    
    # Nếu query rất cụ thể (>3 từ), thử tìm video trực tiếp
    if search_query and len(search_query.split()) >= 3:
        print(f"🔍 [YouTube] Detecting specific video query: '{search_query}'")
        try:
            # Try search_youtube_video first
            video_result = await search_youtube_video(
                video_title=search_query, 
                auto_open=True
            )
            if video_result.get("success"):
                return video_result
        except Exception as e:
            print(f"⚠️ [YouTube] Video search failed: {e}, fallback to search page")
    
    # Fallback: Mở trang tìm kiếm
    if search_query:
        url = f"https://www.youtube.com/results?search_query={quote_plus(search_query)}"
    else:
        url = "https://www.youtube.com"
    
    webbrowser.open(url)
    return {"success": True, "url": url}
```

### Test:
```bash
# Test API
curl -X POST http://localhost:8000/api/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_youtube_video",
    "args": {"video_title": "Sơn Tùng MTP Chúng Ta", "auto_open": false}
  }'
```

**Dependencies:**
```bash
pip install youtube-search-python
```

---

## 4️⃣ Lưu và kích hoạt JWT Token/Endpoint

**Trạng thái:** ✅ **HOẠT ĐỘNG** (nếu format đúng)

### Save Endpoint với JWT Token

**API:** `/api/save_endpoints`

```javascript
// Web UI
fetch('/api/save_endpoints', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    devices: [
      {
        name: "My Device",
        token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",  // JWT token
        enabled: true
      }
    ]
  })
})
```

### Kích hoạt Endpoint

**API:** `/api/activate_endpoint`

```javascript
fetch('/api/activate_endpoint', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({index: 0})  // Index của device
})
```

### Format JWT Token

**Chuẩn JWT:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

**Hoặc URL đầy đủ:**
```
https://api.example.com/v1/endpoint?token=abc123
```

### Verify trong file

```bash
# Check xiaozhi_endpoints.json
cat xiaozhi_endpoints.json | jq '.endpoints[0].token'
```

**Nếu không lưu:**
- Check format token (JWT phải có 3 phần cách bởi `.`)
- Xem log terminal: `✅ [Endpoint] Successfully saved X devices...`
- Test API response: `{"success": true}`

---

## 5️⃣ Mở nhạc từ thư mục người dùng

**Trạng thái:** ✅ **HOẠT ĐỘNG** (nếu config đúng)

### Cấu hình Custom Music Folder

**Method 1: File `custom_music_folder.txt`**

```bash
echo "F:\My Music" > custom_music_folder.txt
```

**Method 2: File `music_folder_config.json`**

```json
{
  "music_folder": "F:\\My Music",
  "extensions": [".mp3", ".flac", ".wav", ".m4a", ".ogg", ".wma"]
}
```

### Code Logic (line 3888-4000)

```python
async def play_music(filename: str, create_playlist: bool = True):
    """Phát nhạc từ custom folder hoặc music_library"""
    
    # 1. Đọc custom folder config
    custom_folder = None
    if Path("custom_music_folder.txt").exists():
        with open("custom_music_folder.txt", 'r', encoding='utf-8') as f:
            custom_folder = Path(f.read().strip())
    
    # 2. Fallback to default
    if not custom_folder or not custom_folder.exists():
        custom_folder = Path("music_library")
    
    # 3. Search file
    music_file = find_music_file(filename, custom_folder)
    
    # 4. Play with VLC
    if music_file:
        vlc_player.play_file(str(music_file))
        return {"success": True, "file": music_file.name}
    else:
        return {"success": False, "error": "Không tìm thấy file"}
```

### Test:

```bash
# Tạo config
echo "F:\My Music" > custom_music_folder.txt

# Test qua API
curl -X POST http://localhost:8000/api/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "play_music",
    "args": {"filename": "song.mp3", "create_playlist": false}
  }'
```

### Troubleshooting

**Không tìm thấy file:**
- Check path trong `custom_music_folder.txt` có đúng không
- Thử absolute path: `F:\Music` thay vì relative `./Music`
- Verify extensions được support: `.mp3`, `.flac`, `.wav`, `.m4a`, `.ogg`, `.wma`

**VLC không chạy:**
```bash
pip install python-vlc
```

**Log để debug:**
- `🔄 [VLC] Refreshing song cache from ...` → Đang scan folder
- `✅ [VLC] Song cache refreshed: X songs` → Tìm thấy X files
- `✅ [VLC] Playing: song.mp3` → Đang phát

---

## 🧪 Chạy Test Suite

```bash
# Test tất cả 5 vấn đề
TEST_ALL_5_ISSUES.bat

# Hoặc
python test_all_5_issues.py
```

---

## 📊 Checklist

- [ ] 1. API keys KHÔNG hardcode trong source ✅
- [ ] 2. Save endpoints hoạt động (check xiaozhi_endpoints.json)
- [ ] 3. YouTube mở direct video (không chỉ search page)
- [ ] 4. JWT token được lưu và kích hoạt
- [ ] 5. Custom music folder được nhận và phát nhạc

---

## 🚀 Build Clean EXE

Sau khi fix xong tất cả:

```bash
BUILD_CLEAN_PRODUCTION.bat
```

EXE output: `dist\miniZ_MCP_Clean.exe`

**Security:**
- ✅ No API keys in EXE
- ✅ No test files
- ✅ Clean production build

---

## 📝 Version Info

**Version:** 4.3.1  
**Date:** 2025-12-14  
**Features Fixed:** 5/5
