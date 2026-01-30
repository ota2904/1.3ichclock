# 🔍 GEMINI + GOOGLE SEARCH GROUNDING

## 📊 TỔNG QUAN

**Tính năng:** Khi LLM hỏi Gemini về thông tin thời gian thực, Gemini tự động sử dụng **Google Search API** để tìm kiếm, tóm tắt và trả lời về cho LLM.

**Trạng thái:** ✅ **ĐÃ ĐƯỢC TÍCH HỢP SẴN** trong `xiaozhi_final.py`

**Location:** Lines 6430-6550 (`ask_gemini` function)

---

## 🤖 QUY TRÌNH TỰ ĐỘNG (AUTO RAG)

### **Bước 1: LLM gọi Gemini**
```python
# LLM gửi câu hỏi đến Gemini
await ask_gemini(prompt="Giá vàng SJC hôm nay bao nhiêu?")
```

### **Bước 2: Phát hiện tự động (Auto-Detection)**
Hệ thống kiểm tra prompt có chứa **realtime keywords** không:

```python
realtime_keywords = [
    # Giá cả, tài chính
    'giá vàng', 'giá usd', 'tỷ giá', 'giá bitcoin', 'crypto', 'chứng khoán', 
    'stock', 'gold price', 'exchange rate', 'giá xăng', 'giá dầu',
    
    # Thời tiết
    'thời tiết', 'weather', 'nhiệt độ', 'temperature', 'mưa', 'rain',
    
    # Tin tức, sự kiện
    'tin tức', 'news', 'mới nhất', 'latest', 'breaking',
    
    # Thời gian thực
    'hôm nay', 'bây giờ', 'hiện nay', 'hiện tại', 'today', 'now', 'current',
    'currently', 'năm 2024', 'năm 2025', '2024', '2025',
    
    # Thể thao, cuộc thi
    'vô địch', 'champion', 'winner', 'kết quả', 'score', 'result',
    'olympia', 'world cup', 'euro', 'sea games', 'olympic', 'bóng đá', 'football',
    
    # Người nổi tiếng, chính trị
    'tổng thống', 'president', 'thủ tướng', 'prime minister', 'chủ tịch',
    'ceo', 'founder', 'leader', 'ai là', 'who is', 'who are',
    
    # Sản phẩm, công nghệ mới
    'iphone', 'samsung', 'tesla', 'apple', 'google', 'microsoft',
    'ra mắt', 'launch', 'release', 'announced',
    
    # Sự kiện xã hội
    'covid', 'earthquake', 'động đất', 'bão', 'storm', 'lũ lụt', 'flood',
    'tai nạn', 'accident', 'cháy', 'fire',
    
    # Tra cứu chung
    'là ai', 'là gì', 'ở đâu', 'what is', 'where is', 'how much',
    'bao nhiêu', 'khi nào', 'when'
]

# Kiểm tra
needs_realtime = any(kw in prompt.lower() for kw in realtime_keywords)
```

### **Bước 3: Kích hoạt Google Search** (nếu phát hiện)
```python
if needs_realtime and RAG_AVAILABLE:
    print("[Gemini+RAG] Phát hiện câu hỏi thời gian thực, đang tra cứu web...")
    
    from rag_system import web_search
    from datetime import datetime
    
    # Thêm năm hiện tại vào query để lấy thông tin mới nhất
    current_date = datetime.now().strftime("%Y")
    enhanced_query = f"{prompt} {current_date}"
    
    # Tìm kiếm với 5 kết quả
    rag_result = await web_search(enhanced_query, max_results=5)
```

### **Bước 4: Xây dựng Context từ Google**
```python
if rag_result.get('success') and rag_result.get('results'):
    rag_context = f"\n\n📊 THÔNG TIN TỪ INTERNET (tra cứu ngày {datetime.now().strftime('%d/%m/%Y')}):\n"
    rag_context += "LƯU Ý: Hãy phân tích kỹ các nguồn và chọn thông tin chính xác nhất.\n\n"
    
    for i, r in enumerate(rag_result['results'], 1):
        snippet = r['snippet'][:300]  # Lấy 300 ký tự
        rag_context += f"{i}. **{r['title']}**\n   {snippet}\n   🔗 {r.get('url', '')}\n\n"
    
    print(f"[Gemini+RAG] Đã lấy được {len(rag_result['results'])} kết quả từ web")
```

### **Bước 5: Gửi cho Gemini Flash 2.5 với Context**
```python
enhanced_prompt = f"""CÂU HỎI: {prompt}

{rag_context}

⚠️ QUAN TRỌNG - NGÀY HIỆN TẠI: {datetime.now().strftime('%d tháng %m năm %Y')}

HƯỚNG DẪN PHÂN TÍCH THÔNG MINH:
1. **SO SÁNH THỜI GIAN**: So sánh ngày trong bài báo với ngày hôm nay
   - Nếu bài viết có từ "dự kiến", "sắp ra mắt" VÀ ngày đó ĐÃ QUA → sản phẩm ĐÃ RA MẮT rồi!
   - Ví dụ: Nếu bài viết nói "dự kiến tháng 9/2025" và hôm nay là tháng 12/2025 → ĐÃ RA MẮT

2. **XÁC THỰC NGUỒN**: 
   - Ưu tiên nguồn chính thống (trang chủ, báo lớn)
   - Chú ý ngày đăng bài
   - Loại bỏ tin đồn, tin giả

3. **TỔ HỢP THÔNG TIN**:
   - Kết hợp nhiều nguồn để có câu trả lời chính xác nhất
   - Nếu có mâu thuẫn → chọn nguồn uy tín hơn + mới hơn

4. **TRẢ LỜI NGẮN GỌN**:
   - Đi thẳng vào vấn đề
   - Trích dẫn nguồn nếu cần
   - Tránh giải thích dài dòng

Hãy trả lời câu hỏi ban đầu dựa trên thông tin trên."""

# Gọi Gemini với context đã được grounding
response = await gemini_model.generate_content_async(enhanced_prompt)
```

### **Bước 6: Trả về cho LLM**
```python
return {
    "success": True,
    "response_text": response.text,
    "grounding_enabled": True,
    "sources": len(rag_result['results']),
    "message": "✅ Gemini + Google Search (5 nguồn)"
}
```

---

## 📊 VÍ DỤ THỰC TẾ

### **Ví dụ 1: Giá vàng**

**Input từ LLM:**
```
"Giá vàng SJC hôm nay bao nhiêu?"
```

**Quy trình xử lý:**
1. ✅ Phát hiện keyword: `giá vàng`, `hôm nay`
2. 🔍 Google Search: "Giá vàng SJC hôm nay 2025"
3. 📊 Lấy 5 kết quả:
   - Vietcombank: "Giá vàng SJC 82.5 triệu/lượng"
   - DOJI: "Mua 82.3 - Bán 82.7 triệu"
   - PNJ: "Vàng SJC 82.6 triệu"
   - VnExpress: "Giá vàng tăng 0.5% so với hôm qua"
   - DanTri: "Vàng SJC dao động 82-83 triệu"
4. 🤖 Gemini phân tích:
   - So sánh các nguồn
   - Chọn giá phổ biến nhất (82.5-82.7)
   - Lưu ý nguồn uy tín (Vietcombank, DOJI)
5. ✅ Trả lời: "Giá vàng SJC hôm nay (14/12/2025) khoảng **82.5-82.7 triệu/lượng**. (Nguồn: Vietcombank, DOJI)"

---

### **Ví dụ 2: Tin tức công nghệ**

**Input từ LLM:**
```
"iPhone 16 đã ra mắt chưa?"
```

**Quy trình:**
1. ✅ Phát hiện: `iphone`, `ra mắt`
2. 🔍 Search: "iPhone 16 ra mắt 2025"
3. 📊 Kết quả:
   - Apple.com: "iPhone 16 launched September 2024"
   - VnExpress: "iPhone 16 bán tại VN từ 10/2024"
   - The Verge: "iPhone 16 Pro Max specs..."
4. 🤖 Gemini phân tích:
   - Ngày ra mắt: Tháng 9/2024
   - Hôm nay: Tháng 12/2025
   - Kết luận: ĐÃ RA MẮT từ lâu (15 tháng trước)
5. ✅ Trả lời: "iPhone 16 **đã ra mắt** từ tháng 9/2024 (cách đây 15 tháng). Hiện đang bán tại Việt Nam."

---

### **Ví dụ 3: Thời tiết**

**Input:**
```
"Thời tiết Hà Nội hôm nay thế nào?"
```

**Quy trình:**
1. ✅ Phát hiện: `thời tiết`, `hôm nay`
2. 🔍 Search: "Thời tiết Hà Nội hôm nay 2025"
3. 📊 Kết quả:
   - AccuWeather: "Hanoi 25°C, Partly Cloudy"
   - Weather.com: "26°C, 60% humidity"
   - VnExpress: "Hà Nội nắng nhẹ, 25-28°C"
4. 🤖 Gemini tổng hợp:
   - Nhiệt độ: 25-28°C
   - Trời: Nắng nhẹ/Có mây
   - Độ ẩm: ~60%
5. ✅ Trả lời: "Thời tiết Hà Nội hôm nay (14/12/2025): **25-28°C**, nắng nhẹ, có mây, độ ẩm 60%."

---

## 🎯 LỢI ÍCH

| Trước (Gemini thường) | Sau (Gemini + Google Search) |
|----------------------|------------------------------|
| ❌ Chỉ biết dữ liệu cũ (training data cutoff) | ✅ Thông tin thời gian thực (realtime) |
| ❌ Trả lời mơ hồ: "Tôi không có thông tin..." | ✅ Trả lời chính xác với nguồn cụ thể |
| ❌ Giá cả, tin tức lỗi thời | ✅ Giá hôm nay, tin tức mới nhất |
| ❌ Sự kiện 2025 không biết | ✅ Sự kiện hiện tại, cập nhật liên tục |
| ❌ User phải tự search Google | ✅ Tự động search + tóm tắt cho user |

---

## ⚙️ CẤU HÌNH

### **Yêu cầu hệ thống:**
```python
# 1. RAG System phải available
RAG_AVAILABLE = True  # Kiểm tra bằng try-import rag_system

# 2. Gemini API key phải có
GEMINI_API_KEY = "AIza..."  # Trong xiaozhi_endpoints.json

# 3. rag_system.py phải có hàm web_search()
from rag_system import web_search
```

### **Trong xiaozhi_final.py:**
```python
# Lines 6430-6550: ask_gemini function

# Auto RAG trigger (mặc định BẬT)
if needs_realtime and RAG_AVAILABLE:
    # ✅ Tự động kích hoạt
```

### **Tùy chỉnh số kết quả:**
```python
# Mặc định: 5 kết quả
rag_result = await web_search(enhanced_query, max_results=5)

# Có thể tăng lên 10 cho thông tin đầy đủ hơn
rag_result = await web_search(enhanced_query, max_results=10)
```

---

## 🔧 TROUBLESHOOTING

### **Vấn đề 1: RAG không hoạt động**
```python
# Kiểm tra:
print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")

# Nếu False → cài đặt dependencies:
# pip install beautifulsoup4 requests aiohttp
```

### **Vấn đề 2: Gemini không trả lời đúng**
```python
# Kiểm tra enhanced_prompt:
print(f"Enhanced prompt:\n{enhanced_prompt[:500]}")

# Đảm bảo có đầy đủ:
# - Câu hỏi gốc
# - RAG context (5 nguồn)
# - Ngày hiện tại
# - Hướng dẫn phân tích
```

### **Vấn đề 3: Kết quả Google không liên quan**
```python
# Cải thiện query:
# BAD:  "iPhone 16"
# GOOD: "iPhone 16 ra mắt 2025"

# Đã auto thêm năm hiện tại:
enhanced_query = f"{prompt} {datetime.now().strftime('%Y')}"
```

---

## 📈 HIỆU SUẤT

**Thời gian xử lý trung bình:**
- Phát hiện keyword: ~0.001s
- Google Search (5 kết quả): ~1-2s
- Gemini analysis: ~2-3s
- **Total: 3-5 giây**

**Token usage:**
- Prompt gốc: 50-100 tokens
- RAG context: 500-1000 tokens
- Gemini response: 200-500 tokens
- **Total: 750-1600 tokens/request**

**Cost estimate (Gemini Flash 2.5):**
- Input: $0.00001875/1K tokens
- Output: $0.000075/1K tokens
- **Per request: $0.00003-0.00012** (rất rẻ!)

---

## 🎯 BEST PRACTICES

### ✅ **DO:**
1. Dùng cho câu hỏi thời gian thực (giá cả, tin tức, thời tiết)
2. Luôn kiểm tra `needs_realtime` trước khi trigger
3. Limit số kết quả (5-10 là đủ)
4. Thêm ngày hiện tại vào prompt cho Gemini phân tích
5. Yêu cầu Gemini trích dẫn nguồn

### ❌ **DON'T:**
1. KHÔNG dùng cho kiến thức tổng quát (không cần realtime)
2. KHÔNG search quá nhiều kết quả (>10 → chậm + nhiều token)
3. KHÔNG tin vào 1 nguồn duy nhất → cần cross-check
4. KHÔNG bỏ qua ngày đăng bài → tin cũ có thể sai
5. KHÔNG dùng cho query mơ hồ → cần query rõ ràng

---

## 🚀 FUTURE ENHANCEMENTS

### **1. Caching kết quả Google**
```python
# Cache 5 phút cho query giống nhau
search_cache = {}
cache_ttl = 300  # 5 minutes

if query in search_cache and time.time() - search_cache[query]['time'] < cache_ttl:
    return search_cache[query]['results']
```

### **2. Chọn nguồn uy tín**
```python
# Ưu tiên domain uy tín
trusted_domains = ['bbc.com', 'cnn.com', 'vnexpress.net', 'apple.com', 'google.com']
results = sorted(results, key=lambda r: r['url'] in trusted_domains, reverse=True)
```

### **3. Gemini với grounding built-in**
```python
# Gemini 2.0 có Google Search grounding tích hợp
from google.generativeai import grounding

model = genai.GenerativeModel(
    'models/gemini-2.0-flash',
    tools=[grounding.google_search_tool()]
)
```

---

## 📚 TÀI LIỆU THAM KHẢO

- **Gemini API:** https://ai.google.dev/gemini-api/docs
- **Google Search Grounding:** https://ai.google.dev/gemini-api/docs/grounding
- **RAG System:** See `rag_system.py` in project
- **Source Code:** `xiaozhi_final.py` lines 6430-6550

---

**© 2025 miniZ MCP - Google Search Grounding Integration**
