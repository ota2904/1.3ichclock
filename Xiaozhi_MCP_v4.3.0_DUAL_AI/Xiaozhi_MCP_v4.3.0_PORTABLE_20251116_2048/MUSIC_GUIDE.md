# 🎵 Hướng Dẫn Sử Dụng Music Library

## 📁 Cấu trúc thư mục
```
music_library/
├── Pop/
│   ├── In Love.mp3
│   ├── chẳng phải tình đầu sao đau đến thế.mp3
│   └── ĐA NGHI.mp3
├── Rock/
└── EDM/
```

## 🎯 4 Cách để AI phát nhạc

### 1️⃣ Phát nhạc ngẫu nhiên (Auto-play all)
**Câu lệnh:**
- "phát nhạc"
- "play music"
- "nghe nhạc đi"

**AI sẽ gọi:** `list_music(auto_play=True)`
- ✅ Tự động phát bài đầu tiên trong thư viện
- Hiển thị tất cả bài hát có sẵn

**Ví dụ response:**
```json
{
  "success": true,
  "files": [3 songs...],
  "message": "✅ Auto-played: In Love.mp3\nTotal 3 song(s) in library",
  "auto_played": true,
  "play_result": {"success": true, "filename": "In Love.mp3"}
}
```

---

### 2️⃣ Phát nhạc theo thư mục (Auto-play by folder)
**Câu lệnh:**
- "phát nhạc Pop"
- "play Pop music"
- "nghe nhạc EDM"

**AI sẽ gọi:** `list_music(subfolder="Pop", auto_play=True)`
- ✅ Tự động phát bài đầu tiên trong thư mục Pop
- Chỉ hiển thị nhạc trong thư mục đó

**Ví dụ response:**
```json
{
  "success": true,
  "files": [3 Pop songs...],
  "message": "✅ Auto-played: In Love.mp3\nTotal 3 song(s) in library",
  "play_result": {"success": true}
}
```

---

### 3️⃣ Tìm và phát theo từ khóa (Search & Auto-play)
**Câu lệnh:**
- "phát bài có từ 'love'"
- "play songs with 'đa nghi'"
- "tìm và phát nhạc 'tình đầu'"

**AI sẽ gọi:** `search_music(keyword="love", auto_play=True)`
- ✅ Tìm tất cả bài có từ 'love' trong tên
- ✅ Tự động phát bài đầu tiên tìm được
- Hỗ trợ tiếng Việt có dấu

**Ví dụ response:**
```json
{
  "success": true,
  "files": [{"filename": "In Love.mp3", ...}],
  "count": 1,
  "keyword": "love",
  "message": "✅ Found & playing: In Love.mp3\nTotal 1 match(es) for 'love'",
  "auto_played": true,
  "play_result": {"success": true}
}
```

---

### 4️⃣ Phát bài cụ thể theo tên (Direct play)
**Câu lệnh:**
- "phát bài 'In Love.mp3'"
- "play 'ĐA NGHI.mp3'"
- "mở nhạc 'chẳng phải tình đầu'"

**AI sẽ gọi:** `play_music(filename="In Love.mp3")`
- ✅ Phát trực tiếp file được chỉ định
- Hỗ trợ nhiều format tìm kiếm:
  - Tên chính xác: `In Love.mp3`
  - Không phân biệt hoa/thường: `in love.mp3`
  - Theo đường dẫn: `Pop/In Love.mp3`
  - Tìm một phần: `love` → tìm `In Love.mp3`

**Ví dụ response:**
```json
{
  "success": true,
  "filename": "In Love.mp3",
  "path": "Pop/In Love.mp3",
  "full_path": "F:\\miniz_pctool\\music_library\\Pop\\In Love.mp3",
  "size_mb": 3.3,
  "message": "✅ Đang phát: In Love.mp3"
}
```

---

## 🛑 Dừng nhạc

**Câu lệnh:**
- "dừng nhạc"
- "stop music"
- "tắt nhạc đi"

**AI sẽ gọi:** `stop_music()`
- Đóng Windows Media Player
- Dừng tất cả nhạc đang phát

---

## 📋 Chỉ xem danh sách (không phát)

### Xem tất cả bài hát
**Câu lệnh:** "cho tôi xem danh sách nhạc"

**AI sẽ gọi:** `list_music(auto_play=False)`

### Tìm kiếm không phát
**Câu lệnh:** "tìm bài có từ 'love' nhưng đừng phát"

**AI sẽ gọi:** `search_music(keyword="love", auto_play=False)`

---

## 🎯 So sánh các tool

| Tool | Mục đích | Auto-play? | Ví dụ |
|------|----------|------------|-------|
| `list_music()` | Liệt kê tất cả/theo folder | ✅ Mặc định | "phát nhạc Pop" |
| `search_music()` | Tìm theo từ khóa | ✅ Mặc định | "phát bài có 'love'" |
| `play_music()` | Phát file cụ thể | ✅ Luôn phát | "phát In Love.mp3" |
| `stop_music()` | Dừng phát nhạc | N/A | "dừng nhạc" |

---

## 🔧 Technical Details

### Supported Formats
- `.mp3`, `.wav`, `.flac`, `.m4a`, `.ogg`, `.wma`, `.aac`

### Search Features
- **Case-insensitive**: `LOVE` = `love` = `Love`
- **Partial match**: `love` matches `In Love.mp3`
- **Vietnamese support**: `đa nghi` matches `ĐA NGHI.mp3`
- **Path search**: `Pop/In Love.mp3` works

### Error Handling
- File not found → Returns available files list
- Empty folder → Suggests adding music
- Invalid format → Shows supported formats

---

## 📝 Examples

### Scenario 1: User wants random music
```
User: "phát nhạc đi"
AI: list_music(auto_play=True)
Result: ✅ Playing "In Love.mp3" (first song in library)
```

### Scenario 2: User wants specific genre
```
User: "tôi muốn nghe nhạc Pop"
AI: list_music(subfolder="Pop", auto_play=True)
Result: ✅ Playing first Pop song
```

### Scenario 3: User searches by keyword
```
User: "phát bài có từ 'đa nghi'"
AI: search_music(keyword="đa nghi", auto_play=True)
Result: ✅ Found & playing "ĐA NGHI.mp3"
```

### Scenario 4: User wants exact song
```
User: "phát bài In Love"
AI: play_music(filename="In Love")
Result: ✅ Playing "In Love.mp3" (partial match)
```

### Scenario 5: User wants to stop
```
User: "dừng nhạc lại"
AI: stop_music()
Result: ✅ Music stopped
```

---

## 🎉 Key Improvements from Reference Code

Based on `xinnan-tech/xiaozhi-esp32-server`:

1. ✅ **Auto-play by default** - No need for AI to call twice
2. ✅ **Flexible search** - Case-insensitive, partial match, path support
3. ✅ **Async execution** - Non-blocking with `loop.run_in_executor()`
4. ✅ **Single call workflow** - Simplified for AI decision-making
5. ✅ **Vietnamese support** - Full Unicode filename support
6. ✅ **Error recovery** - Helpful error messages with suggestions

---

## 🚀 Quick Reference

| User Says | AI Calls | Result |
|-----------|----------|--------|
| "phát nhạc" | `list_music()` | Auto-plays first song |
| "phát nhạc Pop" | `list_music(subfolder="Pop")` | Auto-plays first Pop song |
| "phát bài có 'love'" | `search_music(keyword="love")` | Finds & plays songs with 'love' |
| "phát In Love" | `play_music(filename="In Love")` | Plays "In Love.mp3" |
| "dừng nhạc" | `stop_music()` | Stops music |
| "xem danh sách nhạc" | `list_music(auto_play=False)` | Only lists, doesn't play |

