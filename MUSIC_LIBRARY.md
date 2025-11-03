# 🎵 Music Library Feature - MCP Music Player

## 📋 Tổng Quan

Tính năng Music Library cho phép MCP (Xiaozhi) quản lý và phát nhạc từ thư mục `music_library` trên máy tính.

## 🎯 Mục Đích

- 🎵 Lưu trữ nhạc cá nhân trong thư mục riêng
- 🤖 MCP có thể liệt kê, tìm kiếm và phát nhạc
- 🎚️ Điều khiển phát nhạc thông qua voice commands
- 📁 Tổ chức nhạc theo thư mục con (thể loại)

## 📁 Cấu Trúc Thư Mục

```
miniz_pctool/
└── music_library/          # Thư mục gốc chứa nhạc
    ├── README.md           # Hướng dẫn
    ├── Pop/                # Nhạc Pop
    │   ├── song1.mp3
    │   └── song2.mp3
    ├── Rock/               # Nhạc Rock
    │   └── rock_song.mp3
    ├── Classical/          # Nhạc Classical
    │   └── beethoven.flac
    └── [Tự do tạo folder]
```

## 🎼 Định Dạng Hỗ Trợ

| Format | Extension | Hỗ trợ |
|--------|-----------|--------|
| MP3 | `.mp3` | ✅ |
| WAV | `.wav` | ✅ |
| FLAC | `.flac` | ✅ |
| M4A | `.m4a` | ✅ |
| OGG | `.ogg` | ✅ |
| WMA | `.wma` | ✅ |
| AAC | `.aac` | ✅ |

## 🛠️ API Tools (4 Tools Mới)

### 1. **list_music** - Liệt kê nhạc

**Description:** Liệt kê tất cả file nhạc trong music_library

**Parameters:**
- `subfolder` (string, optional): Tên thư mục con để lọc

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "song1.mp3",
      "path": "Pop/song1.mp3",
      "size_mb": 4.5,
      "extension": ".mp3"
    }
  ],
  "count": 1,
  "library_path": "F:\\miniz_pctool\\music_library",
  "message": "Tìm thấy 1 bài hát"
}
```

**MCP Usage:**
```json
{
  "tool": "list_music",
  "arguments": {}
}

// Hoặc với subfolder
{
  "tool": "list_music",
  "arguments": {
    "subfolder": "Pop"
  }
}
```

---

### 2. **play_music** - Phát nhạc

**Description:** Phát file nhạc từ music_library

**Parameters:**
- `filename` (string, required): Tên file nhạc (VD: "song1.mp3")

**Response:**
```json
{
  "success": true,
  "filename": "song1.mp3",
  "path": "Pop/song1.mp3",
  "size_mb": 4.5,
  "message": "✅ Đang phát: song1.mp3"
}
```

**MCP Usage:**
```json
{
  "tool": "play_music",
  "arguments": {
    "filename": "song1.mp3"
  }
}
```

**Lưu ý:**
- Tự động tìm file trong tất cả subfolder
- Mở bằng Windows Media Player
- Nếu file không tồn tại sẽ báo lỗi

---

### 3. **stop_music** - Dừng nhạc

**Description:** Dừng phát nhạc (đóng Windows Media Player)

**Parameters:** Không có

**Response:**
```json
{
  "success": true,
  "message": "✅ Đã dừng phát nhạc"
}
```

**MCP Usage:**
```json
{
  "tool": "stop_music",
  "arguments": {}
}
```

---

### 4. **search_music** - Tìm kiếm nhạc

**Description:** Tìm kiếm nhạc theo từ khóa trong tên file

**Parameters:**
- `keyword` (string, required): Từ khóa tìm kiếm

**Response:**
```json
{
  "success": true,
  "files": [
    {
      "filename": "love_song.mp3",
      "path": "Pop/love_song.mp3",
      "size_mb": 3.8,
      "extension": ".mp3"
    }
  ],
  "count": 1,
  "keyword": "love",
  "message": "Tìm thấy 1 kết quả cho 'love'"
}
```

**MCP Usage:**
```json
{
  "tool": "search_music",
  "arguments": {
    "keyword": "love"
  }
}
```

---

## 💡 Kịch Bản Sử Dụng

### **Kịch bản 1: Liệt kê tất cả nhạc**
```
User: "Liệt kê tất cả nhạc trong thư viện"
Xiaozhi: Gọi list_music()
Response: "Tìm thấy 15 bài hát"
```

### **Kịch bản 2: Phát nhạc**
```
User: "Phát bài 'summer_vibes.mp3'"
Xiaozhi: Gọi play_music(filename="summer_vibes.mp3")
Response: "✅ Đang phát: summer_vibes.mp3"
```

### **Kịch bản 3: Tìm và phát**
```
User: "Tìm nhạc có từ 'love' và phát bài đầu tiên"
Xiaozhi: 
  1. Gọi search_music(keyword="love")
  2. Lấy filename từ kết quả
  3. Gọi play_music(filename=...)
Response: "✅ Đang phát: love_song.mp3"
```

### **Kịch bản 4: Dừng nhạc**
```
User: "Dừng nhạc"
Xiaozhi: Gọi stop_music()
Response: "✅ Đã dừng phát nhạc"
```

### **Kịch bản 5: Lọc theo thể loại**
```
User: "Liệt kê nhạc Pop"
Xiaozhi: Gọi list_music(subfolder="Pop")
Response: "Tìm thấy 8 bài hát"
```

---

## 📝 Hướng Dẫn Sử Dụng

### **Bước 1: Thêm nhạc vào thư mục**

1. Mở thư mục `music_library`
2. Copy file nhạc vào thư mục gốc hoặc subfolder
3. Có thể tạo subfolder mới để phân loại

**Ví dụ:**
```bash
music_library/
├── favorite.mp3           # Trực tiếp trong gốc
├── Pop/
│   ├── song1.mp3
│   └── song2.mp3
└── EDM/                   # Tự tạo folder mới
    └── remix.mp3
```

### **Bước 2: Kiểm tra nhạc**

Chạy script test:
```bash
python test_music.py
```

Hoặc từ MCP:
```json
{
  "tool": "list_music",
  "arguments": {}
}
```

### **Bước 3: Phát nhạc**

Từ MCP:
```json
{
  "tool": "play_music",
  "arguments": {
    "filename": "song1.mp3"
  }
}
```

---

## ⚙️ Cấu Hình

### **Thư mục mặc định:**
```python
MUSIC_LIBRARY = Path(__file__).parent / "music_library"
```

### **Định dạng hỗ trợ:**
```python
MUSIC_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma', '.aac'}
```

### **Player mặc định:**
Windows Media Player (wmplayer.exe)

---

## 🔧 Technical Details

### **File Detection:**
- Sử dụng `Path.rglob()` để tìm file trong tất cả subfolder
- Case-insensitive extension matching
- Tự động tạo thư mục nếu chưa tồn tại

### **Music Playback:**
- Dùng `os.startfile()` để mở file với app mặc định
- Windows Media Player sẽ được sử dụng
- Hỗ trợ tất cả format mà WMP hỗ trợ

### **Stop Mechanism:**
- Dùng PowerShell để kill process `wmplayer.exe`
- Force stop với `-Force` flag
- Silent error với `-ErrorAction SilentlyContinue`

---

## 🎯 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| list_music() | < 0.5s | Depends on file count |
| play_music() | < 0.2s | Instant open |
| stop_music() | < 0.3s | Kill process |
| search_music() | < 0.5s | Linear search |

---

## 🚀 Future Enhancements (Optional)

- [ ] Playlist management
- [ ] Shuffle mode
- [ ] Volume control for music
- [ ] Play next/previous
- [ ] Music metadata (ID3 tags)
- [ ] Music duration info
- [ ] Create/save playlists

---

## 📊 Summary

### **Đã Thêm:**
- ✅ 4 tools mới: `list_music`, `play_music`, `stop_music`, `search_music`
- ✅ Thư mục `music_library` với cấu trúc subfolder
- ✅ Hỗ trợ 7 định dạng nhạc phổ biến
- ✅ Script test `test_music.py`
- ✅ Documentation đầy đủ

### **Total Tools:** 35 tools (31 → 35)

### **Ready for:**
- 🎵 Phát nhạc từ voice commands
- 🔍 Tìm kiếm và phát nhạc thông minh
- 📁 Quản lý thư viện nhạc cá nhân
- 🤖 Integration hoàn chỉnh với MCP/Xiaozhi

---

**Version:** 4.1.0  
**Feature:** Music Library  
**Date:** November 3, 2025  
**Status:** ✅ Ready for Production
