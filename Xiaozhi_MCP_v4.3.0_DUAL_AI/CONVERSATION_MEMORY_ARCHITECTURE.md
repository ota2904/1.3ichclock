# 🧠 KIẾN TRÚC BỘ NHỚ HỘI THOẠI - XIAOZHI & MINIZ MCP

## 📋 Tổng quan

Cách các hệ thống AI hiện đại (Xiaozhi, miniZ MCP) lưu trữ và quản lý bộ nhớ hội thoại ngắn hạn.

---

## 🏗️ KIẾN TRÚC HIỆN TẠI (miniZ MCP v4.3.0)

### 1. **Cấu trúc lưu trữ đa tầng**

```
📁 AppData/Local/miniZ_MCP/conversations/
├── conversation_history.json          # File tổng hợp (backward compatible)
├── conversation_2025-12-07.json      # File theo ngày
├── conversation_2025-12-06.json
└── user_profile.json                 # Profile người dùng
```

### 2. **Cấu trúc dữ liệu Message**

```python
message = {
    "role": "user" | "assistant" | "system" | "tool",
    "content": "Nội dung tin nhắn",
    "timestamp": "2025-12-07 19:14:13",
    "metadata": {
        "session_id": "20251207",
        "tool_called": "play_music",      # Nếu có
        "confidence": 0.85,               # Nếu có
        "source": "smart_analyzer",       # Nguồn gốc
        "device_id": "device_1"           # Multi-device
    }
}
```

### 3. **Quản lý Memory (xiaozhi_final.py)**

#### **Global Variables**
```python
conversation_history = []              # List lưu tất cả messages
conversation_sessions = {}             # Sessions theo ngày
```

#### **Storage Locations**
```python
CONVERSATION_BASE_DIR = "~/AppData/Local/miniZ_MCP/conversations"
CONVERSATION_FILE = "conversation_history.json"
USER_PROFILE_FILE = "user_profile.json"
```

---

## 🔧 CÁC FUNCTION CHÍNH

### **1. load_conversation_history()**
```python
def load_conversation_history():
    """Load lịch sử hội thoại từ file"""
    global conversation_history
    
    # 1. Load file tổng hợp
    if CONVERSATION_FILE.exists():
        conversation_history = json.load(file)
    
    # 2. Load file hôm nay
    today_file = get_today_conversation_file()
    if today_file.exists():
        today_data = json.load(today_file)
        # Merge với history
```

**✅ Chạy lúc:** Server startup (line 966)

---

### **2. save_conversation_history()**
```python
def save_conversation_history():
    """Lưu lịch sử hội thoại (tổng hợp + theo ngày)"""
    
    # 1. Lưu file tổng hợp
    json.dump(conversation_history, CONVERSATION_FILE)
    
    # 2. Lưu file theo ngày
    today_messages = [msg for msg in conversation_history 
                      if msg["timestamp"].startswith(today)]
    
    today_data = {
        "date": "2025-12-07",
        "total_messages": len(today_messages),
        "messages": today_messages,
        "last_updated": "2025-12-07 19:14:13"
    }
    
    json.dump(today_data, today_file)
```

**✅ Chạy khi:**
- Auto-save sau mỗi 3 messages
- Server shutdown
- User export

---

### **3. add_to_conversation()**
```python
def add_to_conversation(role, content, metadata=None):
    """Thêm message vào lịch sử"""
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(),
        "metadata": metadata or {}
    }
    
    conversation_history.append(message)
    
    # Auto-save sau mỗi 3 messages
    if len(conversation_history) % 3 == 0:
        save_conversation_history()
    
    # Cập nhật user profile
    if role == "user":
        update_user_profile_from_message(content, metadata)
```

**📊 Auto-save trigger:** Mỗi 3 messages = 1 lần save

---

## 🎯 SMART CONVERSATION ANALYZER

### **Class SmartConversationAnalyzer (line 13347-13800)**

```python
class SmartConversationAnalyzer:
    def __init__(self):
        self.conversation_history = []     # Lịch sử 20 messages gần nhất
        self.max_history = 20              # Giới hạn buffer
        self.last_executed_tool = None     # Tool cuối cùng
        self.last_tool_result = None       # Kết quả cuối cùng
```

#### **Memory Buffer (20 messages)**
```python
def add_message(self, role, content, tool_called=None):
    """Thêm message vào buffer"""
    message = {
        "role": role,
        "content": content,
        "tool_called": tool_called,
        "timestamp": datetime.now().isoformat()
    }
    
    self.conversation_history.append(message)
    
    # Giữ tối đa 20 messages
    if len(self.conversation_history) > self.max_history:
        self.conversation_history = self.conversation_history[-self.max_history:]
```

**🔄 Rolling buffer:** Luôn giữ 20 messages gần nhất

---

## 📡 API ENDPOINTS

### **1. GET /api/conversation/history**
```json
{
    "success": true,
    "history": [
        {
            "role": "user",
            "content": "phát nhạc đi",
            "tool_called": null,
            "timestamp": "2025-12-07T19:14:13.601526"
        },
        {
            "role": "assistant",
            "content": "Đang phát nhạc...",
            "tool_called": "play_music",
            "timestamp": "2025-12-07T19:14:13.602452"
        }
    ],
    "length": 4
}
```

---

### **2. POST /api/conversation/add**
```json
{
    "role": "user",
    "content": "bài tiếp theo",
    "metadata": {
        "device_id": "device_1"
    }
}
```

**Response:**
```json
{
    "success": true,
    "message": "Message added successfully"
}
```

---

### **3. POST /api/conversation/clear**
```json
{
    "success": true,
    "message": "Conversation history cleared"
}
```

---

### **4. POST /api/smart_analyze**
```json
{
    "user_query": "bài tiếp theo",
    "llm_response": "OK đã chuyển bài",
    "conversation_history": [
        {"role": "user", "content": "phát nhạc"},
        {"role": "assistant", "content": "Đang phát"}
    ],
    "auto_execute": true,
    "use_ai": false
}
```

**🧠 Smart Analyzer sử dụng conversation_history để:**
- Hiểu context ("bài" → đang nói về nhạc)
- Phân tích ý định ("tiếp theo" → music_next)
- Theo dõi flow (user → LLM → tool → result)

---

## 🔄 LUỒNG HOẠT ĐỘNG

### **Kịch bản 1: User gửi tin nhắn**
```
1. User: "phát nhạc đi"
   ↓
2. add_to_conversation("user", "phát nhạc đi")
   ↓
3. conversation_history.append({...})
   ↓
4. Smart Analyzer phân tích → play_music
   ↓
5. Tool execution → VLC player
   ↓
6. add_to_conversation("assistant", "Đang phát nhạc", {"tool_called": "play_music"})
   ↓
7. Auto-save (nếu đủ 3 messages)
```

---

### **Kịch bản 2: LLM trả lời text-only**
```
1. User: "bài tiếp theo"
   ↓
2. LLM: "OK đã chuyển bài" (KHÔNG gọi tool)
   ↓
3. Smart Analyzer detect:
   - user_query: ""
   - llm_response: "OK đã chuyển bài"
   - conversation_history: [{user: "phát nhạc"}, {assistant: "đang phát"}]
   ↓
4. Pattern matching: "chuyển bài" → music_next
   ↓
5. Auto-execute: music_next()
   ↓
6. add_to_conversation("assistant", "OK đã chuyển bài", {"tool_called": "music_next"})
```

---

## 💾 LƯU TRỮ & PERSISTENCE

### **Multi-file Strategy**

#### **1. File tổng hợp (conversation_history.json)**
```json
[
    {
        "role": "user",
        "content": "phát nhạc",
        "timestamp": "2025-12-07 10:00:00",
        "metadata": {"session_id": "20251207"}
    },
    {
        "role": "assistant",
        "content": "Đang phát nhạc",
        "timestamp": "2025-12-07 10:00:01",
        "metadata": {"tool_called": "play_music"}
    }
]
```

**📦 Dung lượng:** Không giới hạn (có thể rất lớn)

---

#### **2. File theo ngày (conversation_2025-12-07.json)**
```json
{
    "date": "2025-12-07",
    "total_messages": 156,
    "messages": [...],
    "last_updated": "2025-12-07 19:14:13"
}
```

**📦 Ưu điểm:**
- Dễ tìm kiếm theo ngày
- Giảm tải file lớn
- Backup theo ngày

---

#### **3. User Profile (user_profile.json)**
```json
{
    "total_interactions": 1543,
    "last_active": "2025-12-07 19:14:13",
    "favorite_tools": {
        "play_music": 234,
        "volume_up": 89,
        "calculator": 45
    },
    "preferences": {
        "music_genre": "pop",
        "default_volume": 80
    }
}
```

**🎯 Mục đích:**
- Học thói quen người dùng
- Cá nhân hóa trải nghiệm
- Analytics

---

## ⚡ PERFORMANCE OPTIMIZATION

### **1. Rolling Buffer (20 messages)**
```python
self.max_history = 20

if len(self.conversation_history) > self.max_history:
    self.conversation_history = self.conversation_history[-20:]
```

**💡 Lý do:** 
- Giảm memory usage
- Faster processing
- Context vẫn đủ cho phân tích

---

### **2. Auto-save Strategy**
```python
if len(conversation_history) % 3 == 0:
    save_conversation_history()
```

**💡 Balance:**
- ✅ Không mất data (save thường xuyên)
- ✅ Không lag (không save mỗi message)
- ⚖️ Sweet spot: Mỗi 3 messages

---

### **3. Lazy Loading**
```python
def load_conversation_history():
    # Only load khi cần
    if CONVERSATION_FILE.exists():
        conversation_history = json.load(f)
```

**💡 Server startup nhanh hơn**

---

## 🌐 MULTI-DEVICE SYNC

### **Session Management**
```python
message["metadata"]["session_id"] = datetime.now().strftime("%Y%m%d")
message["metadata"]["device_id"] = "device_1"
```

### **Sync Strategy**
```
Device 1 (PC) ──┐
                 ├──→ Central Server (API) ──→ conversation_history.json
Device 2 (Phone) ┘
```

**🔄 Real-time sync:**
- WebSocket for instant updates
- HTTP API for polling
- File-based for offline

---

## 📊 SO SÁNH VỚI XIAOZHI CONSOLE

### **Điểm giống**
✅ Lưu tất cả messages (không filter)  
✅ Multi-session support  
✅ User profile tracking  
✅ Tool execution logging  
✅ Timestamp cho mọi message  

### **Điểm khác**
| Feature | miniZ MCP | Xiaozhi Console |
|---------|-----------|-----------------|
| Storage | Local files (JSON) | Cloud database |
| Sync | File-based | Real-time API |
| Analytics | Basic (user_profile.json) | Advanced (dashboard) |
| Multi-user | ❌ Single user | ✅ Team support |
| Privacy | 🔒 100% local | ☁️ Cloud-based |

---

## 🔐 PRIVACY & SECURITY

### **Local-first Architecture**
```
✅ Tất cả data lưu local
✅ Không upload lên cloud
✅ User có full control
✅ Không cần internet để access history
```

### **File Permissions**
```
📁 ~/AppData/Local/miniZ_MCP/
   ├── conversations/          (Only current user)
   │   ├── *.json             (UTF-8, 644)
   └── user_profile.json       (UTF-8, 644)
```

---

## 🎓 BEST PRACTICES

### **1. Message Structure**
```python
# ✅ GOOD: Complete metadata
message = {
    "role": "user",
    "content": "phát nhạc",
    "timestamp": "2025-12-07T19:14:13.601526",
    "metadata": {
        "session_id": "20251207",
        "device_id": "device_1",
        "source": "smart_analyzer"
    }
}

# ❌ BAD: Missing metadata
message = {
    "role": "user",
    "content": "phát nhạc"
}
```

---

### **2. Context Window**
```python
# ✅ GOOD: Recent 20 messages
def get_recent_context(max_messages=20):
    return conversation_history[-max_messages:]

# ❌ BAD: Toàn bộ history (có thể quá lớn)
context = conversation_history  # 1000+ messages!
```

---

### **3. Save Frequency**
```python
# ✅ GOOD: Auto-save mỗi 3 messages
if len(conversation_history) % 3 == 0:
    save_conversation_history()

# ❌ BAD: Save mỗi message (quá chậm)
conversation_history.append(msg)
save_conversation_history()  # Every time!
```

---

## 📈 ANALYTICS & INSIGHTS

### **API: GET /api/conversation/stats**
```json
{
    "total_messages": 1543,
    "today_messages": 156,
    "most_used_tools": [
        {"tool": "play_music", "count": 234},
        {"tool": "volume_up", "count": 89}
    ],
    "peak_hours": [
        {"hour": 14, "messages": 45},
        {"hour": 20, "messages": 78}
    ]
}
```

---

## 🚀 FUTURE ENHANCEMENTS

### **1. Vector Database Integration**
```python
# Semantic search trong history
results = vector_db.search("tìm lúc tôi hỏi về nhạc pop")
```

### **2. AI-powered Summarization**
```python
# Tóm tắt session
summary = ai.summarize(conversation_history[-50:])
# "User đã nghe 5 bài nhạc pop và tăng âm lượng 3 lần"
```

### **3. Export to Cloud (Optional)**
```python
# Backup to Google Drive / OneDrive
export_to_cloud(conversation_history, provider="gdrive")
```

---

## 📝 SUMMARY

### **Key Takeaways**

1. **🎯 Multi-file Strategy**
   - File tổng hợp + file theo ngày
   - Balance giữa performance và persistence

2. **⚡ Rolling Buffer**
   - 20 messages gần nhất cho Smart Analyzer
   - Full history lưu disk

3. **🔄 Auto-save**
   - Mỗi 3 messages = 1 lần save
   - Không mất data, không lag

4. **🔐 Local-first**
   - 100% privacy
   - Không phụ thuộc internet

5. **🧠 Smart Context**
   - Conversation history giúp AI hiểu context
   - Tool execution logging

---

## 📚 REFERENCES

- **Code Location:** `xiaozhi_final.py` (lines 685-966)
- **Smart Analyzer:** `SmartConversationAnalyzer` class (lines 13347-13800)
- **API Endpoints:** Lines 13803-13900
- **Test Suite:** `TEST_SMART_ANALYZER.py`
- **Documentation:** `SMART_ANALYZER_GUIDE.md`

---

**📅 Last Updated:** December 7, 2025  
**👤 Author:** miniZ MCP Development Team  
**📦 Version:** 4.3.0 DUAL AI
