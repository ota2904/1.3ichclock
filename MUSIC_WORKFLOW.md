# 🎵 Music Library - AI Workflow Guide

## Vấn đề đã Fix
**Triệu chứng:** MCP/AI tìm được file nhạc (list_music thành công) nhưng không phát được (không gọi play_music)

**Nguyên nhân:** 
1. Response của `list_music` chưa đủ rõ ràng cho AI hiểu phải làm gì tiếp theo
2. Description của tools chưa nhấn mạnh đủ về workflow 2 bước
3. AI không biết cách extract filename từ response JSON

## Giải pháp

### 1. Improved Response Message
**Trước:**
```json
{
  "message": "Tìm thấy 1 bài hát",
  "files": [{"filename": "song.mp3", ...}]
}
```

**Sau:**
```json
{
  "message": "Tìm thấy 1 bài hát. To play music, use play_music tool with exact filename from the list below:\n  - song.mp3",
  "files": [{"filename": "song.mp3", ...}],
  "instruction": "Use play_music(filename) with exact filename from files list"
}
```

### 2. Stronger Tool Descriptions

**list_music:**
```
REQUIRED: Call this FIRST before play_music! Returns list with 'files' array containing objects with 'filename' field. Use the exact 'filename' value from response to call play_music next. Example workflow: 1) call list_music(), 2) get filename from response.files[0].filename, 3) call play_music(filename=that_filename).
```

**play_music:**
```
MUST call list_music FIRST to get exact filename! After calling list_music, copy the 'filename' value from response.files[0].filename and pass it here. Example: if list_music returns files[0].filename='song.mp3', then call play_music(filename='song.mp3'). DO NOT make up filename - ALWAYS use exact value from list_music response!
```

### 3. Clear Parameter Description

```python
"filename": {
    "description": "EXACT filename from list_music response (e.g., response.files[0].filename). Copy the complete filename including extension. Example: 'my_song.mp3' or 'Pop/my_song.mp3'"
}
```

## Correct Workflow for AI

```javascript
// Step 1: List available music
const listResult = await mcp.call("list_music");
// Response: {
//   "files": [
//     {"filename": "chẳng phải tình đầu sao đau đến thế.mp3", ...}
//   ],
//   "message": "Tìm thấy 1 bài hát. To play music, use play_music tool with exact filename from the list below:\n  - chẳng phải tình đầu sao đau đến thế.mp3"
// }

// Step 2: Extract exact filename
const filename = listResult.files[0].filename;
// filename = "chẳng phải tình đầu sao đau đến thế.mp3"

// Step 3: Play the music
const playResult = await mcp.call("play_music", {filename: filename});
// Response: {
//   "success": true,
//   "message": "✅ Đang phát: chẳng phải tình đầu sao đau đến thế.mp3"
// }
```

## Key Improvements

1. ✅ **Explicit Instructions** - Message tells AI exactly what to do next
2. ✅ **Show Filenames** - List filenames directly in message (up to 10 files)
3. ✅ **Example Workflow** - Description shows step-by-step process
4. ✅ **Emphasized Keywords** - MUST, FIRST, EXACT, DO NOT make up
5. ✅ **JSON Path Examples** - `response.files[0].filename` shows how to extract

## Testing

```bash
# Test list_music response
python -c "import asyncio; from xiaozhi_final import list_music; result = asyncio.run(list_music()); print(result['message'])"

# Output:
# Tìm thấy 1 bài hát. To play music, use play_music tool with exact filename from the list below:
#   - chẳng phải tình đầu sao đau đến thế.mp3

# Test play_music
python -c "import asyncio; from xiaozhi_final import play_music; print(asyncio.run(play_music('chẳng phải tình đầu sao đau đến thế.mp3')))"

# Output:
# {'success': True, 'message': '✅ Đang phát: ...'}
```

## For Users

Khi yêu cầu AI phát nhạc, hãy nói rõ ràng:

❌ **Không tốt:**
- "Phát nhạc"
- "Bật nhạc lên"

✅ **Tốt:**
- "Liệt kê nhạc và phát bài đầu tiên"
- "Tìm nhạc và phát bài có từ 'love'"
- "Show me music list then play the first song"

## Status
✅ All improvements committed and server running
🎯 AI should now understand the 2-step workflow correctly
📊 Logging enabled to track tool calls in terminal
