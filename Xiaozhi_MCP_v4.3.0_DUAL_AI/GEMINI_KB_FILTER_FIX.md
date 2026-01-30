# Sửa lỗi Gemini Knowledge Base Context Filtering

## 📋 Vấn đề đã phát hiện

Khi sử dụng tính năng lọc thông tin cơ sở dữ liệu bằng Gemini, hàm `get_knowledge_context` có các vấn đề:

1. **Tóm tắt quá ngắn**: Gemini trả về tóm tắt quá ngắn (50-100 chars) không đủ thông tin cho LLM
2. **Prompt quá dài**: Prompt yêu cầu 300-600 từ nhưng chỉ cho 500 output tokens, không đủ
3. **Không có fallback**: Khi Gemini tóm tắt quá ngắn, vẫn sử dụng kết quả đó thay vì fallback sang content gốc
4. **Context quá dài**: Lấy 3000-4000 chars mỗi document, vượt khả năng xử lý của LLM

## ✅ Giải pháp đã áp dụng

### 1. Tối ưu Prompt (tham khảo từ `web_search` trong `rag_system.py`)

**Trước:**
```python
# Prompt dài dòng, yêu cầu 300-600 từ
# Lấy 3000-4000 chars mỗi document
```

**Sau:**
```python
# Prompt ngắn gọn, súc tích
# Chỉ yêu cầu 200-400 từ (phù hợp với web_search: ~300-500 chars/snippet)
# Lấy 2000-3000 chars mỗi document (vừa đủ thông tin)
```

### 2. Điều chỉnh `max_output_tokens`

**Trước:** `max_output_tokens=500` → Không đủ cho 300-600 từ

**Sau:** `max_output_tokens=800` → Đủ cho 200-400 từ (≈ 600-1200 chars)

### 3. Thêm Validation & Fallback

**Trước:**
```python
if response and response.text:
    content = f"[📝 Tóm tắt bởi Gemini]\n{response.text}"
```

**Sau:**
```python
if response and response.text:
    summarized = response.text.strip()
    
    # ⚠️ KIỂM TRA: Nếu tóm tắt quá ngắn (< 150 chars), dùng content gốc
    if len(summarized) < 150:
        print(f"⚠️ [Gemini] Summary too short, using original")
        content = content[:2500] + "\n\n[... Nội dung tiếp bị cắt ...]"
    else:
        content = f"[📝 Tóm tắt bởi Gemini]\n{summarized}"
```

### 4. Error Handling chi tiết hơn

```python
except Exception as e:
    print(f"⚠️ [Gemini] Summarization error: {e}")
    import traceback
    print(f"⚠️ [Gemini] Traceback: {traceback.format_exc()}")
    
    # Kiểm tra các lỗi phổ biến
    error_msg = str(e).lower()
    if "rate limit" in error_msg or "quota" in error_msg:
        print(f"⚠️ [Gemini] API rate limit/quota exceeded")
    elif "api key" in error_msg:
        print(f"⚠️ [Gemini] API key invalid")
    elif "timeout" in error_msg:
        print(f"⚠️ [Gemini] Request timeout")
    
    # Fallback: dùng content gốc
    content = content[:2500] + "\n\n[... Nội dung tiếp bị cắt ...]"
```

## 📊 Kết quả Test

### Test 1: Query rỗng (lấy TẤT CẢ documents)
```
✅ SUCCESS
Total documents: 6
Documents included: 6  
Context length: 9,777 chars (phù hợp cho LLM)
⚠️ Gemini summary too short → đã fallback sang original content
```

### Test 2: Query cụ thể ("Lê Trung Khoa")
```
✅ SUCCESS
Total documents: 3 (filtered)
Documents included: 3
Context length: 2,860 chars (tối ưu)
Keywords used: ['trung', 'khoa']
```

### Test 3: Query phổ biến ("thông tin")
```
✅ SUCCESS  
Total documents: 4 (filtered)
Documents included: 4
Context length: 4,391 chars (tốt)
Keywords used: ['thông', 'tin']
```

## 🎯 Độ dài hợp lý cho LLM

Dựa trên phân tích `web_search` trong `rag_system.py`:

| Thành phần | Độ dài khuyến nghị | Lý do |
|------------|-------------------|-------|
| **Snippet mỗi kết quả** | 300-500 chars | Đủ thông tin, không quá dài |
| **Context tổng** | 2,000-10,000 chars | Phụ thuộc vào số lượng documents |
| **Gemini summary** | 200-400 từ (≈ 600-1200 chars) | Cô đọng, súc tích, giữ thông tin quan trọng |
| **Max output tokens** | 800 tokens | Đủ cho 200-400 từ tiếng Việt |

## 🔧 Files đã sửa

1. **xiaozhi_final.py** - Hàm `get_knowledge_context`:
   - Tối ưu prompt (ngắn gọn hơn, rõ ràng hơn)
   - Giảm content input: 3000→2000 chars (có query), 4000→3000 chars (không query)
   - Tăng max_output_tokens: 500→800
   - Thêm validation: kiểm tra tóm tắt < 150 chars → fallback
   - Thêm error handling chi tiết với các loại lỗi phổ biến
   - Fallback content length: 3000→2500 chars

## 🧪 Test Files

1. **test_gemini_kb_filter.py** - Test cơ bản với 4 scenarios
2. **test_gemini_kb_debug.py** - Test chi tiết với edge cases và Gemini API trực tiếp

## 📝 Lưu ý

- Hệ thống **LUÔN** thử tóm tắt bằng Gemini trước (nếu content > 2000 chars)
- Nếu tóm tắt quá ngắn hoặc lỗi → tự động fallback sang original content
- Original content được cắt ở 2500 chars để đảm bảo không quá tải LLM
- Tham khảo thiết kế từ `web_search` trong `rag_system.py` để đảm bảo consistency

## ✅ Trạng thái

**HOÀN THÀNH** - Tất cả tests đều PASS, hệ thống hoạt động ổn định với:
- ✅ Tóm tắt thông minh (fallback khi cần)
- ✅ Độ dài context hợp lý cho LLM
- ✅ Error handling tốt
- ✅ Consistency với các module khác (rag_system)

---

📅 **Ngày:** 17/12/2025  
👤 **Người thực hiện:** GitHub Copilot + User
