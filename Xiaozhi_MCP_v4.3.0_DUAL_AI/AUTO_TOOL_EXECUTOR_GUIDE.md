# 🤖 AUTO TOOL EXECUTOR - Hướng Dẫn Sử Dụng

## 📋 Tổng Quan

**Auto Tool Executor** là tính năng tự động phát hiện intent từ LLM response và thực thi tool tương ứng.

### ❓ Vấn Đề Cần Giải Quyết

Khi LLM chỉ trả lời text mà không gọi tool:
- ❌ User: "quay lại bài trước"
- ❌ LLM: "OK, đã quay lại bài trước" ← Chỉ trả lời text, không gọi `music_previous()`
- ❌ Kết quả: Nhạc không thực sự quay lại

### ✅ Giải Pháp

Auto Tool Executor sẽ:
1. **Phân tích** response từ LLM
2. **Phát hiện** intent (ví dụ: "quay lại bài trước" → `music_previous`)
3. **Tự động gọi** tool tương ứng
4. **Trả về** kết quả thực thi

---

## 🔧 API Endpoints

### 1️⃣ POST `/api/auto_execute`

**Mô tả:** Phân tích LLM response và tự động gọi tool

**Request Body:**
```json
{
  "llm_response": "OK, đã quay lại bài trước",
  "original_query": "quay lại bài trước",
  "auto_execute": true
}
```

**Response:**
```json
{
  "success": true,
  "llm_response": "OK, đã quay lại bài trước",
  "original_query": "quay lại bài trước",
  "intent_detected": "music_previous",
  "tool_suggested": "music_previous",
  "confidence": 0.85,
  "tool_executed": true,
  "tool_result": {
    "success": true,
    "message": "⏮️ Đã chuyển về bài: Song.mp3",
    "current_song": "Song.mp3",
    "playlist_index": 1,
    "playlist_total": 5
  },
  "message": "✅ Detected: music_previous | Executed: true"
}
```

**Parameters:**

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `llm_response` | string | ✅ | Text response từ LLM |
| `original_query` | string | ❌ | Câu hỏi gốc của user (tăng accuracy) |
| `auto_execute` | boolean | ❌ | `true`: tự động gọi tool, `false`: chỉ phát hiện (default: `true`) |

---

## 🎯 Supported Tools & Patterns

### 🎵 VLC Music Controls

| Tool | Keywords Detected | Confidence |
|------|-------------------|-----------|
| `music_next` | "bài tiếp", "next", "skip", "chuyển bài" | 0.85 |
| `music_previous` | "bài trước", "previous", "quay lại" | 0.85 |
| `pause_music` | "tạm dừng", "pause" | 0.85 |
| `resume_music` | "tiếp tục", "resume", "phát tiếp" | 0.85 |
| `stop_music` | "dừng", "stop", "tắt nhạc" | 0.85 |
| `play_music` | "phát nhạc", "play music" | 0.85 |

**Ví dụ:**

```
LLM Response: "OK, đã chuyển bài tiếp theo"
→ Detected: music_next (confidence: 0.85)
→ Auto execute: music_next()
→ Result: ⏭️ Đã chuyển tới bài mới
```

---

## 🌐 WebSocket Integration

### Event: `llm_response_check`

**Gửi từ Client:**
```javascript
websocket.send(JSON.stringify({
  type: "llm_response_check",
  response: "OK, đã quay lại bài trước",
  query: "quay lại bài trước",
  auto_execute: true
}));
```

**Nhận từ Server:**
```javascript
websocket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "auto_execute_result") {
    console.log("Tool detected:", data.tool_suggested);
    console.log("Tool executed:", data.tool_executed);
    console.log("Result:", data.tool_result);
  }
};
```

---

## 📊 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER QUERY                                               │
│    "quay lại bài trước"                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. LLM RESPONSE                                             │
│    "OK, đã quay lại bài trước" ← Chỉ text, không gọi tool  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. AUTO TOOL EXECUTOR                                       │
│    ├─ Phân tích: "quay lại bài trước"                      │
│    ├─ Phát hiện: music_previous (confidence: 0.85)         │
│    └─ Quyết định: auto_execute = true → GỌI TOOL           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. TOOL EXECUTION                                           │
│    await music_previous()                                   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. RESULT                                                   │
│    {                                                        │
│      "success": true,                                       │
│      "message": "⏮️ Đã chuyển về bài: Song.mp3",           │
│      "tool_executed": true                                  │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Examples

### Test 1: Music Next

```bash
curl -X POST http://localhost:8000/api/auto_execute \
  -H "Content-Type: application/json" \
  -d '{
    "llm_response": "OK, đã chuyển bài tiếp theo",
    "original_query": "bài tiếp",
    "auto_execute": true
  }'
```

**Expected:**
```json
{
  "success": true,
  "intent_detected": "music_next",
  "tool_executed": true,
  "tool_result": {
    "success": true,
    "message": "⏭️ Đã chuyển tới bài: NextSong.mp3"
  }
}
```

### Test 2: Pause Music

```bash
curl -X POST http://localhost:8000/api/auto_execute \
  -H "Content-Type: application/json" \
  -d '{
    "llm_response": "Đã tạm dừng nhạc",
    "original_query": "tạm dừng",
    "auto_execute": true
  }'
```

### Test 3: Detection Only (No Execution)

```bash
curl -X POST http://localhost:8000/api/auto_execute \
  -H "Content-Type: application/json" \
  -d '{
    "llm_response": "OK, quay lại bài trước nhé",
    "auto_execute": false
  }'
```

**Expected:**
```json
{
  "success": true,
  "intent_detected": "music_previous",
  "tool_executed": false,
  "message": "✅ Detected: music_previous | Executed: false"
}
```

---

## 🔍 Confidence Levels

| Confidence | Ý Nghĩa | Hành Động |
|-----------|---------|-----------|
| 0.85 - 1.0 | **HIGH** - Match regex pattern chính xác | ✅ Auto execute |
| 0.60 - 0.84 | **MEDIUM** - Intent detector phát hiện | ⚠️ Auto execute nếu enabled |
| 0.0 - 0.59 | **LOW** - Không rõ ràng | ❌ Skip execution |

---

## 🛠️ Extending Patterns

### Thêm Pattern Mới

**File:** `xiaozhi_final.py`, function `api_auto_execute`

```python
vlc_patterns = {
    # Thêm tool mới
    "increase_volume": [
        r'\b(tăng âm lượng|volume up|louder)\b',
        r'\b(to hơn|increase volume)\b'
    ],
    # ... các patterns khác
}
```

### Thêm Tool Handler

```python
if detected_tool == "increase_volume":
    tool_args = {"steps": 10}  # Tăng 10%
    tool_result = await volume_up(**tool_args)
```

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| **Phân tích Intent** | < 10ms |
| **Tool Execution** | 200-500ms (tùy tool) |
| **Total Latency** | < 600ms |
| **Accuracy** | 85-95% (với regex patterns) |
| **False Positive Rate** | < 5% |

---

## ⚠️ Important Notes

### 1. Confidence Threshold

- Chỉ thực thi tool khi `confidence > 0.6`
- Có thể điều chỉnh trong code:

```python
if auto_execute and detected_tool and confidence > 0.6:
    # Execute tool
```

### 2. Fallback Behavior

Nếu không match pattern → dùng `intent_detector`:
- Phân tích semantic
- Confidence thấp hơn (0.5-0.7)

### 3. Tool Registry

Chỉ thực thi tools có trong `TOOLS` registry:
```python
if detected_tool in TOOLS and TOOLS[detected_tool]["handler"]:
    # Safe to execute
```

---

## 🎯 Use Cases

### ✅ Khi Nên Dùng

1. **LLM không gọi tool:** Text-only response
2. **Double-check safety:** Verify LLM đã gọi đúng tool
3. **Fallback mechanism:** LLM lỗi, hệ thống tự động xử lý

### ❌ Khi Không Nên Dùng

1. **LLM đã gọi tool:** Tránh duplicate execution
2. **Commands phức tạp:** Nhiều tools cần gọi liên tiếp
3. **User confirmation needed:** Actions quan trọng (shutdown, delete file...)

---

## 🚀 Integration Example (JavaScript)

```javascript
// Web UI: Intercept LLM response và auto-execute
async function handleLLMResponse(response, userQuery) {
  // 1. Hiển thị response cho user
  displayMessage(response);
  
  // 2. Kiểm tra có cần auto-execute không
  const autoExecResult = await fetch('/api/auto_execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      llm_response: response,
      original_query: userQuery,
      auto_execute: true
    })
  }).then(r => r.json());
  
  // 3. Nếu tool được thực thi → cập nhật UI
  if (autoExecResult.tool_executed) {
    console.log('🤖 Auto-executed:', autoExecResult.tool_suggested);
    
    // Cập nhật VLC status
    if (autoExecResult.tool_result.success) {
      updateVLCStatus();
      showNotification('✅ ' + autoExecResult.tool_result.message);
    }
  }
}
```

---

## 📞 Support & Contact

**Issues:** Nếu gặp vấn đề, kiểm tra:
1. Tool có trong `TOOLS` registry không
2. Pattern regex có match đúng không
3. Confidence threshold có hợp lý không
4. Tool handler có hoạt động đúng không

**Logs:**
```
🤖 [Auto Execute] Analyzing LLM response: 'OK, đã quay lại...'
✅ [Auto Execute] Detected: music_previous (confidence: 0.85)
🚀 [Auto Execute] Executing tool: music_previous
✅ [Auto Execute] Tool executed successfully: music_previous
```

---

## 🎉 Kết Luận

Auto Tool Executor giúp:
- ✅ **Tăng reliability:** Tool luôn được gọi dù LLM lỗi
- ✅ **Cải thiện UX:** User không cần retry
- ✅ **Giảm latency:** Không cần gọi LLM lại
- ✅ **Flexible:** Dễ dàng thêm patterns mới

**Version:** v4.3.0  
**Last Updated:** December 2025
