# 🤖 AUTO DOCUMENT PROCESSING WITH GEMINI

## Tính năng mới: Tự động xử lý tài liệu với Gemini 2.5 Flash

### 📋 Mô tả

Khi người dùng hỏi về **cơ sở dữ liệu** hoặc **tài liệu** (PDF, Word, TXT, JSON, XML), hệ thống sẽ:

1. ✅ **Tự động phát hiện** ý định người dùng
2. ✅ **Tìm kiếm** tài liệu liên quan trong Knowledge Base
3. ✅ **Gửi cho Gemini 2.5** để xử lý nội dung
4. ✅ **Trả về** câu trả lời đã được Gemini phân tích

### 🎯 Kích hoạt tự động khi có keywords:

- `cơ sở dữ liệu`, `database`, `CSDL`, `DB`
- `tài liệu`, `document`, `file`, `files`
- `PDF`, `Word`, `TXT`, `JSON`, `XML`, `CSV`
- `trong file`, `từ file`, `ở file`
- `knowledge base`, `kiến thức`, `tri thức`
- `đọc file`, `xem file`, `tìm trong`
- `thông tin trong`, `dữ liệu trong`

### 📝 Ví dụ sử dụng

#### 1. Hỏi về cơ sở dữ liệu:
```
User: "Cho tôi biết thông tin về khách hàng trong cơ sở dữ liệu"
```
→ Tự động tìm các file liên quan và gửi cho Gemini xử lý

#### 2. Hỏi về tài liệu cụ thể:
```
User: "Tóm tắt nội dung trong file báo cáo tháng 11"
```
→ Tìm file "báo cáo tháng 11" và Gemini sẽ tóm tắt

#### 3. Tìm kiếm trong documents:
```
User: "Tìm trong tài liệu xem có thông tin về pricing không?"
```
→ Gemini sẽ đọc tất cả documents và trả lời

### 🔧 API Endpoint

**POST** `/api/smart_chat`

```json
{
  "query": "Cho tôi biết thông tin trong database về sản phẩm",
  "model": "models/gemini-2.5-flash"
}
```

**Response:**
```json
{
  "success": true,
  "query": "Cho tôi biết thông tin trong database về sản phẩm",
  "response": "Dựa trên tài liệu, có 3 sản phẩm chính: ...",
  "intent": "document_query",
  "tool_used": "auto_process_document_with_gemini",
  "documents_found": [
    {
      "file_name": "products.json",
      "file_path": "data/products.json"
    }
  ],
  "model": "models/gemini-2.5-flash",
  "auto_document_processing": true
}
```

### 🚀 Cách test

#### 1. Chuẩn bị Knowledge Base:

```bash
# Index một thư mục chứa documents
curl -X POST http://localhost:8000/api/knowledge/index_directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "C:/Documents/my_data"}'
```

#### 2. Test query:

```bash
# Hỏi về database
curl -X POST http://localhost:8000/api/smart_chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Cho tôi biết thông tin trong cơ sở dữ liệu",
    "model": "models/gemini-2.5-flash"
  }'
```

#### 3. Hoặc test từ Web UI:

1. Mở http://localhost:8000
2. Gõ: "Tìm trong tài liệu xem có thông tin gì về khách hàng"
3. Hệ thống tự động kích hoạt Gemini để xử lý

### ⚙️ Flow xử lý

```
User Query
    ↓
[Auto Detect Keywords]
    ↓ (có keyword về documents/database)
[Search Knowledge Base]
    ↓
[Load Documents Content]
    ↓
[Send to Gemini 2.5 Flash]
    ↓
[Gemini Analyzes & Responds]
    ↓
[Return to User]
```

### 🎁 Lợi ích

✅ **Tự động** - Không cần gọi tool thủ công  
✅ **Thông minh** - Gemini hiểu context và trả lời chính xác  
✅ **Nhanh** - Dùng Gemini 2.5 Flash (siêu nhanh)  
✅ **Chính xác** - Trích dẫn từ documents thực tế  
✅ **Tiện lợi** - User chỉ cần hỏi tự nhiên  

### 📊 Kết quả mẫu

**Input:**
```
"Trong cơ sở dữ liệu có bao nhiêu khách hàng VIP?"
```

**Output:**
```
Dựa trên tài liệu "customers.json", hiện có 127 khách hàng VIP, 
được phân loại theo 3 tier:
- Gold: 45 khách hàng
- Platinum: 58 khách hàng  
- Diamond: 24 khách hàng

Nguồn: customers.json, section "vip_customers"
```

### 🔍 Debug & Logs

Check console để xem flow:
```
📊 [Auto Document] Detected document query: Trong cơ sở dữ liệu...
📚 [Auto Document] Found 3 documents
✅ [Auto Document] Success! Documents: 3
```

### 💡 Tips

- **Index trước**: Cần index documents vào knowledge base trước
- **Keywords rõ ràng**: Càng nhiều keywords về documents/database, càng dễ kích hoạt
- **Model choice**: Dùng `gemini-2.5-flash` cho tốc độ, `gemini-2.5-pro` cho chất lượng

---

**Version**: 4.3.1  
**Feature**: Auto Document Processing with Gemini  
**Status**: ✅ Active  
