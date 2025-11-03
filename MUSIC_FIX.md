# 🎵 Music Library - Improvements Log

## Inspired by mcp-calculator (github.com/78/mcp-calculator)

Tham khảo từ dự án MCP Calculator để cải thiện tool descriptions và schema.

## Cải tiến #1: Async Executor (✅ Hoàn thành)
**Vấn đề:** Hàm `play_music()` gọi `os.startfile()` (blocking) trực tiếp trong async context.

**Giải pháp:**
```python
# Sử dụng run_in_executor để chạy blocking function
import asyncio
loop = asyncio.get_event_loop()
await loop.run_in_executor(None, os.startfile, str(music_path))
```

## Cải tiến #2: Enhanced Logging (✅ Hoàn thành)
Thêm logging chi tiết để debug:

```python
# Trong handle_xiaozhi_message() - tool call handler:
print(f"🔧 [Tool Call] {tool_name} with args: {args}")
print(f"✅ [Tool Result] {tool_name}: {result}")
```

```python
# Trong play_music():
print(f"🎵 [Play Music] Tìm file: '{filename}'")
print(f"🎵 [Play Music] Đã tìm thấy: {music_path}")
```

## Cải tiến #3: Flexible File Search (✅ Hoàn thành)
Cải thiện tìm kiếm file để hỗ trợ nhiều trường hợp:

1. **Exact match** - Tìm chính xác tên file
2. **Case-insensitive** - Không phân biệt hoa thường
3. **Relative path** - Hỗ trợ path đầy đủ như "Pop/song.mp3"
4. **Partial match** - Tìm theo một phần tên
5. **Error suggestions** - Hiển thị danh sách file có sẵn khi không tìm thấy

```python
# Ví dụ các cách gọi đều hoạt động:
await play_music("song.mp3")                    # Exact
await play_music("SONG.MP3")                    # Case-insensitive
await play_music("Pop/song.mp3")                # With path
await play_music("song")                        # Partial
```

## Cải tiến #4: Better Tool Descriptions (✅ Hoàn thành)
Cải thiện tool descriptions theo phong cách FastMCP để AI hiểu rõ hơn:

**Trước:**
```python
"play_music": {
    "description": "Phát nhạc từ music_library",
    "parameters": {
        "filename": {"description": "Tên file nhạc", ...}
    }
}
```

**Sau:**
```python
"play_music": {
    "description": "Phát file nhạc từ thư viện music_library bằng Windows Media Player. ALWAYS use 'list_music' tool first to get the exact filename, then use this tool to play. Accepts filename (e.g., 'song.mp3') or path (e.g., 'Pop/song.mp3'). The search is case-insensitive and supports partial matching.",
    "parameters": {
        "filename": {
            "description": "Tên file nhạc CHÍNH XÁC từ kết quả list_music (ví dụ: 'my_song.mp3' hoặc 'Pop/my_song.mp3'). Use exact filename from list_music result.",
            ...
        }
    }
}
```

## Cải tiến #5: Function Docstrings (✅ Hoàn thành)
Thêm docstrings chi tiết với examples:

```python
async def play_music(filename: str) -> dict:
    """
    Phát nhạc từ music_library bằng Windows Media Player.
    
    IMPORTANT: Always use 'list_music' first to get exact filename!
    
    Args:
        filename: Exact filename from list_music (e.g., 'song.mp3' or 'Pop/song.mp3')
        
    Returns:
        dict with 'success', 'filename', 'path', 'size_mb', 'message'
        
    Examples:
        play_music("my_song.mp3") -> Plays the file
        play_music("Pop/my_song.mp3") -> Plays file from Pop folder
        
    Note: Search is case-insensitive and supports partial matching
    """
```

## Key Learning từ mcp-calculator

1. **Clear Instructions** - Sử dụng "ALWAYS" và "IMPORTANT" để nhấn mạnh workflow
2. **Examples in Description** - Đưa ví dụ cụ thể ngay trong description
3. **Explicit Format** - Chỉ rõ format input/output (e.g., 'song.mp3', 'Pop/song.mp3')
4. **Workflow Guidance** - Hướng dẫn AI phải dùng tool A trước tool B
5. **Case-insensitive Note** - Nêu rõ tính năng tìm kiếm linh hoạt

## Test Results
✅ **Function test thành công:**
```bash
🎵 [Play Music] Tìm file: 'chẳng phải tình đầu sao đau đến thế.mp3'
🎵 [Play Music] Đã tìm thấy: F:\miniz_pctool\music_library\Pop\chẳng phải tình đầu sao đau đến thế.mp3
{'success': True, 'filename': '...', 'path': 'Pop\\...', 'size_mb': 11.04}
```

## Debug Guide
Khi MCP gọi `play_music`, kiểm tra log sẽ thấy:

```
🔧 [Tool Call] play_music with args: {'filename': '...'}
🎵 [Play Music] Tìm file: '...'
🎵 [Play Music] Đã tìm thấy: ...
✅ [Tool Result] play_music: {...}
```

Nếu có lỗi:
```
❌ [Play Music] Error: ...
❌ Error calling play_music: ...
[Full traceback]
```

## Music Library Tools

### 1. list_music(subfolder="")
Liệt kê file nhạc. **Luôn gọi tool này trước khi play!**

**Description:** "Liệt kê tất cả file nhạc trong thư viện music_library. Sử dụng tool này để xem danh sách nhạc có sẵn trước khi phát. Returns list of music files with filename, path, and size."

### 2. play_music(filename)
Phát nhạc. **Phải dùng tên file chính xác từ list_music!**

**Description:** "Phát file nhạc từ thư viện music_library bằng Windows Media Player. ALWAYS use 'list_music' tool first to get the exact filename, then use this tool to play."

### 3. stop_music()
Dừng nhạc đang phát.

**Description:** "Dừng phát nhạc hiện tại bằng cách đóng Windows Media Player. Use this tool to stop any currently playing music."

### 4. search_music(keyword)
Tìm kiếm nhạc theo từ khóa.

**Description:** "Tìm kiếm file nhạc theo từ khóa trong tên file. Returns matching music files. Use this before play_music to find songs by keyword."

## Usage Examples từ MCP/Xiaozhi

```javascript
// Workflow đúng: List -> Play
1. await mcp.call("list_music")
   // -> {"files": [{"filename": "my_song.mp3", ...}]}

2. await mcp.call("play_music", {filename: "my_song.mp3"})
   // -> {"success": true, "message": "✅ Đang phát: ..."}

// Hoặc: Search -> Play
1. await mcp.call("search_music", {keyword: "love"})
   // -> {"files": [...]}

2. await mcp.call("play_music", {filename: "love_song.mp3"})
   // -> {"success": true, ...}

// Dừng nhạc
await mcp.call("stop_music")
```

## Status
✅ **Tất cả cải tiến hoàn thành**
- Async execution
- Enhanced logging
- Flexible search
- Better descriptions
- Detailed docstrings

🔍 **Logging enabled** - Debug dễ dàng qua terminal
📚 **AI-friendly descriptions** - Theo chuẩn FastMCP/mcp-calculator
