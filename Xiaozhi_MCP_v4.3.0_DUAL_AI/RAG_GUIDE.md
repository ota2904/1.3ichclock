# 🔍 RAG System - Retrieval Augmented Generation

## Giới thiệu

**RAG (Retrieval Augmented Generation)** là hệ thống giúp AI tra cứu thông tin THỜI GIAN THỰC từ Internet và tài liệu nội bộ TRƯỚC KHI trả lời, đảm bảo câu trả lời luôn cập nhật và chính xác.

## Tính năng

### 🌐 DuckDuckGo Search
- Tìm kiếm thông tin mới nhất từ Internet
- Cache thông minh (30 phút)
- Hỗ trợ tiếng Việt và tiếng Anh

### 📚 Local Knowledge Base
- Tìm kiếm trong tài liệu nội bộ của bạn
- TF-IDF ranking cho kết quả chính xác
- Hỗ trợ: TXT, PDF, DOCX, MD, JSON

### 🔄 Hybrid RAG
- Kết hợp cả Web và Local
- Tự động chọn nguồn phù hợp
- Reranking thông minh

---

## Các Tools Mới

### 1. `web_search` - Tìm kiếm Internet
```
Triggers: giá vàng, tin tức, thời tiết, tỷ giá, mới nhất, hôm nay
```

**Ví dụ:**
- "Giá vàng hôm nay bao nhiêu?" → Tự động tra cứu DuckDuckGo
- "Tin tức công nghệ mới nhất?" → Lấy kết quả từ web

### 2. `get_realtime_info` - Thông tin thời gian thực
```
BẮT BUỘC dùng khi hỏi về: tin tức, giá cả, thời tiết, sự kiện đang diễn ra
```

**Ví dụ:**
- "Thời tiết Hà Nội hôm nay?" → Tra cứu thời tiết real-time
- "Tỷ giá USD bây giờ?" → Lấy tỷ giá mới nhất

### 3. `rag_search` - Tìm kiếm Hybrid
```
sources: "web", "local", "hybrid", "auto"
```

**Ví dụ:**
- Tìm cả trên web và trong tài liệu nội bộ
- Kết hợp kết quả với weighted scoring

### 4. `smart_answer` - AI tự chọn nguồn
```
AI phân tích câu hỏi và quyết định nguồn tốt nhất
```

**Ví dụ:**
- Câu hỏi về tin tức → Chọn web
- Câu hỏi về tài liệu công ty → Chọn local

---

## Cách hoạt động

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER HỎI CÂU HỎI                             │
│                          ↓                                       │
│      ┌────────────────────────────────────────────┐             │
│      │   RAG Engine phân tích keywords            │             │
│      │   - "giá", "tin tức" → Web Search          │             │
│      │   - "tài liệu", "file" → Local KB          │             │
│      │   - Không rõ → Hybrid Search               │             │
│      └────────────────────────────────────────────┘             │
│                          ↓                                       │
│  ┌─────────────────┐              ┌─────────────────┐           │
│  │ DuckDuckGo API  │              │ Local Knowledge │           │
│  │   (Internet)    │              │     Base        │           │
│  └────────┬────────┘              └────────┬────────┘           │
│           ↓                                ↓                     │
│      ┌────────────────────────────────────────────┐             │
│      │         Hybrid Reranking                   │             │
│      │    (Web: 40% + Local: 60% weight)         │             │
│      └────────────────────────────────────────────┘             │
│                          ↓                                       │
│      ┌────────────────────────────────────────────┐             │
│      │   Build Context cho LLM                    │             │
│      │   - Web results với sources                │             │
│      │   - Local results với file paths           │             │
│      └────────────────────────────────────────────┘             │
│                          ↓                                       │
│      ┌────────────────────────────────────────────┐             │
│      │   LLM TRẢ LỜI dựa trên context mới        │             │
│      │   (Thông tin cập nhật + chính xác)        │             │
│      └────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Cấu hình

### File: `rag_config.json`

```json
{
  "web_search": {
    "enabled": true,
    "max_results": 5,
    "cache_ttl_minutes": 30,
    "timeout_seconds": 10,
    "region": "vn-vi"
  },
  "knowledge_base": {
    "enabled": true,
    "folder_path": "F:\\thư viện kiến thức",
    "max_results": 5
  },
  "hybrid": {
    "web_weight": 0.4,
    "local_weight": 0.6
  }
}
```

---

## Các câu hỏi mẫu

### Thông tin thời gian thực:
- "Giá vàng SJC hôm nay?"
- "Thời tiết Sài Gòn bây giờ?"
- "Tin tức bóng đá mới nhất?"
- "Tỷ giá USD/VND hôm nay?"

### Tài liệu nội bộ:
- "Tìm trong tài liệu về hợp đồng ABC"
- "Dự án XYZ có bao nhiêu giai đoạn?"
- "Thông tin khách hàng Nguyễn Văn A"

### Kết hợp:
- "So sánh thông tin trong file với giá thị trường hiện tại"

---

## Yêu cầu

### Dependencies:
```
pip install ddgs  # DuckDuckGo Search
# hoặc
pip install duckduckgo-search
```

### Files:
- `rag_system.py` - Module chính
- `rag_config.json` - Cấu hình
- `rag_cache.json` - Cache tự động

---

## Troubleshooting

### Web search không hoạt động:
1. Kiểm tra kết nối mạng
2. Thử lại sau vài giây (rate limit)
3. Fallback sẽ tự động dùng HTML scraping

### Local KB trống:
1. Đảm bảo `knowledge_config.json` có `folder_path`
2. Index lại bằng cách restart server
3. Kiểm tra file trong thư mục có được hỗ trợ

---

## Ưu điểm của RAG

| Không có RAG | Có RAG |
|--------------|--------|
| Kiến thức cũ (training cutoff) | Thông tin mới nhất từ Internet |
| Không biết dữ liệu cá nhân | Tra cứu tài liệu nội bộ |
| Trả lời chung chung | Trả lời chính xác với nguồn |
| Có thể sai lệch | Đảm bảo độ chính xác |

---

**miniZ MCP v4.3.0** - RAG System © 2025
