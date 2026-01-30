# 🎵 Music Library

## Mục đích
Thư mục này chứa nhạc để MCP (Xiaozhi) có thể đọc và phát trên máy tính.

## Hướng dẫn sử dụng

### 1. Thêm nhạc vào thư mục
- Copy file nhạc (MP3, WAV, FLAC, M4A, OGG) vào thư mục này
- Hoặc tạo subfolder để tổ chức theo thể loại

### 2. Sử dụng từ MCP/Xiaozhi

#### Liệt kê tất cả bài hát:
```json
{
  "tool": "list_music",
  "arguments": {}
}
```

#### Phát nhạc:
```json
{
  "tool": "play_music",
  "arguments": {
    "filename": "song.mp3"
  }
}
```

#### Dừng nhạc:
```json
{
  "tool": "stop_music",
  "arguments": {}
}
```

## Định dạng hỗ trợ
- ✅ MP3
- ✅ WAV
- ✅ FLAC
- ✅ M4A
- ✅ OGG
- ✅ WMA

## Ví dụ cấu trúc
```
music_library/
├── Pop/
│   ├── song1.mp3
│   └── song2.mp3
├── Rock/
│   └── rock_song.mp3
└── Classical/
    └── beethoven.mp3
```
