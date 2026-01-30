# 🤖📚 GEMINI AI + KNOWLEDGE BASE

## Tính năng mới: Gemini AI tự động sử dụng Knowledge Base

Khi bạn nhấn nút **"Hỏi Gemini AI + KB"**, Gemini sẽ:
1. ✅ **Tự động tìm kiếm** trong Knowledge Base của bạn
2. ✅ **Đọc toàn bộ tài liệu** liên quan
3. ✅ **Trả lời dựa trên dữ liệu** có sẵn
4. ✅ **Trích dẫn nguồn** cụ thể

---

## 🎯 Cách sử dụng

### Bước 1: Index tài liệu vào Knowledge Base

```bash
# Option 1: Qua Web UI
1. Mở trình duyệt: http://localhost:8000
2. Vào tab "Knowledge Base"
3. Chọn thư mục chứa tài liệu
4. Click "Index Directory"

# Option 2: Qua API
POST /api/knowledge/index_directory
{
  "directory": "F:/Documents/MyData"
}
```

### Bước 2: Hỏi Gemini AI

```bash
# Qua Web UI
1. Click nút "🤖📚 Hỏi Gemini AI + KB"
2. Nhập câu hỏi
3. Gemini tự động tìm trong KB và trả lời

# Qua API
POST /api/tool/ask_gemini
{
  "prompt": "Công ty có bao nhiêu sản phẩm?",
  "model": "models/gemini-2.5-flash"
}
```

---

## 💡 Ví dụ thực tế

### Ví dụ 1: Hỏi về sản phẩm

**Knowledge Base có file:** `products.txt`
```
Sản phẩm A - Phần mềm quản lý
Giá: 5.000.000 VNĐ
Tính năng: Quản lý kho, bán hàng
```

**User hỏi:** "Sản phẩm A có giá bao nhiêu?"

**Gemini trả lời:**
```
Theo tài liệu products.txt, Sản phẩm A - Phần mềm quản lý 
có giá 5.000.000 VNĐ.

Tính năng chính:
- Quản lý kho
- Bán hàng
- Báo cáo

📚 Trả lời dựa trên Knowledge Base của bạn
```

### Ví dụ 2: Hỏi về khách hàng

**Knowledge Base có file:** `customers.txt`
```
Công ty XYZ - Bán lẻ
Doanh thu: 500 triệu
Sản phẩm: A, B

Công ty DEF - Sản xuất  
Doanh thu: 800 triệu
Sản phẩm: A, C
```

**User hỏi:** "Khách hàng nào có doanh thu cao nhất?"

**Gemini trả lời:**
```
Dựa trên dữ liệu trong customers.txt, khách hàng có doanh thu 
cao nhất là Công ty DEF với 800 triệu đồng/năm.

Thông tin chi tiết:
- Ngành: Sản xuất
- Sản phẩm sử dụng: A, C
- Doanh thu: 800 triệu đồng

📚 Trả lời dựa trên Knowledge Base của bạn
```

### Ví dụ 3: Hỏi về dữ liệu không có

**User hỏi:** "Có bao nhiêu nhân viên?"

**Gemini trả lời:**
```
Xin lỗi, tôi không tìm thấy thông tin về số lượng nhân viên 
trong cơ sở dữ liệu hiện tại.

Để tôi có thể trả lời, vui lòng thêm file chứa thông tin 
nhân viên vào Knowledge Base.
```

---

## 🔧 Cấu hình

### File types được hỗ trợ

```
✅ Text files: .txt, .md, .log
✅ Documents: .pdf, .docx, .doc
✅ Data: .json, .xml, .csv
✅ Code: .py, .js, .java, .cpp
✅ Web: .html, .htm
```

### Giới hạn

```
- Max file size: 10MB/file
- Max context length: 50,000 characters
- Max files per directory: 1,000 files
- Supported encodings: UTF-8, UTF-16, Latin-1
```

---

## 🎨 UI Changes

### Trước (Old)
```
🤖 Hỏi Gemini AI
```

### Sau (New)  
```
🤖📚 Hỏi Gemini AI + KB
```

Khi click:
```
🤖 Hỏi Gemini AI + 📚 Knowledge Base
(Gemini sẽ tự động tìm trong cơ sở dữ liệu của bạn)
```

---

## 🧪 Test

Chạy test để kiểm tra:

```bash
# Test tính năng
TEST_GEMINI_KB.bat

# Hoặc
python test_gemini_kb_integration.py
```

Test sẽ:
1. Tạo mock documents (products, customers, revenue)
2. Index vào Knowledge Base
3. Hỏi Gemini 5 câu hỏi
4. Verify Gemini sử dụng KB data

---

## 📊 API Response Format

```json
{
  "success": true,
  "response": "Câu trả lời từ Gemini...",
  "knowledge_base_used": true,
  "model": "models/gemini-2.5-flash",
  "message": "✅ Trả lời dựa trên Knowledge Base của bạn"
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Thành công hay không |
| `response` | string | Câu trả lời của Gemini |
| `knowledge_base_used` | boolean | KB có được dùng không |
| `model` | string | Model Gemini đã dùng |
| `message` | string | Thông báo bổ sung |

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| KB Search Time | < 1s |
| Gemini Response Time | 5-15s |
| Total Time | 6-16s |
| Context Length | Up to 50K chars |

---

## 🔒 Security

```
✅ Dữ liệu KB chỉ ở local machine
✅ Không upload lên Google server
✅ Chỉ gửi context cần thiết cho Gemini
✅ API key không bị log
```

---

## 🐛 Troubleshooting

### KB không có dữ liệu?

```bash
# Check KB status
GET /api/knowledge/search?query=test

# Re-index
POST /api/knowledge/index_directory
{"directory": "your/path"}
```

### Gemini không dùng KB?

Check response có `knowledge_base_used: true` không:

```javascript
// Web UI console
fetch('/api/tool/ask_gemini', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    prompt: "test",
    model: "models/gemini-2.5-flash"
  })
}).then(r => r.json()).then(console.log)
```

### Response quá chậm?

Giảm max_chars trong code:

```python
# xiaozhi_final.py line ~14970
kb_result = await get_knowledge_context(
    query="",
    max_chars=20000,  # Giảm từ 50000 → 20000
    use_gemini_summary=True
)
```

---

## 📝 Changelog

**Version 4.3.1** (2024-12-14)
- ✅ Added auto KB integration for Gemini
- ✅ Updated UI: "Hỏi Gemini AI" → "Hỏi Gemini AI + KB"
- ✅ KB always enabled (không cần bật thủ công)
- ✅ Enhanced prompt with KB context
- ✅ Added `knowledge_base_used` flag in response

---

## 🚀 Next Steps

1. Index tài liệu của bạn vào KB
2. Thử hỏi Gemini về nội dung trong tài liệu
3. Kiểm tra response có icon 📚 không
4. Enjoy! 🎉
