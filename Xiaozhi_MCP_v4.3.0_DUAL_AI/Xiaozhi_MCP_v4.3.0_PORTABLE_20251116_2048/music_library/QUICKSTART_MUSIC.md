# 🎵 Quick Start - Music Library

## 🚀 Bắt Đầu Nhanh

### 1. Thêm Nhạc
```bash
# Copy file nhạc vào thư mục music_library
music_library/
├── my_song.mp3
├── Pop/
│   └── pop_song.mp3
└── Rock/
    └── rock_song.flac
```

### 2. Từ MCP/Xiaozhi

#### Liệt kê tất cả nhạc:
```
"Liệt kê tất cả nhạc"
→ Tool: list_music()
```

#### Phát nhạc:
```
"Phát bài my_song.mp3"
→ Tool: play_music(filename="my_song.mp3")
```

#### Tìm kiếm:
```
"Tìm nhạc có từ 'love'"
→ Tool: search_music(keyword="love")
```

#### Dừng:
```
"Dừng nhạc"
→ Tool: stop_music()
```

## 📋 4 Tools Mới

| Tool | Mô tả | Parameters |
|------|-------|------------|
| **list_music** | Liệt kê nhạc | subfolder (optional) |
| **play_music** | Phát nhạc | filename (required) |
| **stop_music** | Dừng nhạc | - |
| **search_music** | Tìm kiếm | keyword (required) |

## 🎼 Định Dạng Hỗ Trợ

✅ MP3, WAV, FLAC, M4A, OGG, WMA, AAC

## 🔥 Ví Dụ Voice Commands

```
"Phát nhạc Pop"
→ list_music(subfolder="Pop") + play_music(first_result)

"Tìm và phát nhạc có từ relax"
→ search_music(keyword="relax") + play_music(first_result)

"Dừng nhạc và liệt kê tất cả"
→ stop_music() + list_music()
```

## 📖 Chi Tiết

Xem file `MUSIC_LIBRARY.md` để biết thêm chi tiết!

---

**Total Tools:** 35 (Added: +4 music tools)  
**Ready:** ✅ Production
