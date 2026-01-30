# 🧠 Hướng Dẫn Sử Dụng GPT-4 (OpenAI)

## 📋 Tổng quan

Xiaozhi MCP Control Panel đã tích hợp **OpenAI GPT-4** - mô hình AI mạnh mẽ nhất hiện nay. Bạn có thể dùng **CẢ Gemini VÀ GPT-4** trong cùng một hệ thống!

---

## 🆚 So sánh: Gemini vs GPT-4

| Feature | Gemini (Google) | GPT-4 (OpenAI) |
|---------|-----------------|----------------|
| **Giá** | 🆓 MIỄN PHÍ | 💰 TRẢ PHÍ |
| **Quota** | 1500 requests/day | Không giới hạn (trả theo usage) |
| **Knowledge cutoff** | ~10/2024 | ~04/2024 |
| **Tốc độ** | ⚡⚡⚡ Rất nhanh | ⚡⚡ Trung bình |
| **Chất lượng** | ⭐⭐⭐⭐ Rất tốt | ⭐⭐⭐⭐⭐ Xuất sắc |
| **Code generation** | ⭐⭐⭐ Tốt | ⭐⭐⭐⭐⭐ Tuyệt vời |
| **Reasoning** | ⭐⭐⭐ Tốt | ⭐⭐⭐⭐⭐ Siêu mạnh |
| **Tiếng Việt** | ⭐⭐⭐⭐ Tốt | ⭐⭐⭐⭐ Tốt |

---

## 💰 Pricing (GPT-4)

### **Models & Pricing:**

| Model | Input | Output | Use Case |
|-------|-------|--------|----------|
| **gpt-4o** | $2.50/1M tokens | $10/1M tokens | ✅ **Khuyến nghị** - Cân bằng giá & chất lượng |
| **gpt-4-turbo** | $10/1M tokens | $30/1M tokens | Chất lượng cao nhất |
| **gpt-3.5-turbo** | $0.50/1M tokens | $1.50/1M tokens | Rẻ nhất, nhanh |

**Ước tính:**
- 1 câu hỏi ~200 tokens = ~$0.001 (gpt-4o)
- 100 câu hỏi ~$0.10
- 1000 câu hỏi ~$1

**Free trial:** $5 credit cho tài khoản mới!

---

## 🔑 Lấy OpenAI API Key

### **Bước 1: Đăng ký/Đăng nhập**

1. Truy cập: https://platform.openai.com
2. Đăng nhập hoặc đăng ký tài khoản
3. Nạp tiền (hoặc dùng $5 credit free)

### **Bước 2: Tạo API Key**

1. Vào: https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Đặt tên: "Xiaozhi MCP"
4. Copy key (dạng: `sk-proj-...` hoặc `sk-...`)
5. **Lưu lại** (chỉ hiện 1 lần!)

### **Bước 3: Nạp vào Settings**

**Qua Web UI (KHUYẾN NGHỊ):**
1. Mở http://localhost:8000
2. Click ⚙️ (Settings)
3. Cuộn xuống "🧠 OpenAI API Key (GPT-4)"
4. Paste API key
5. Đợi 1 giây → Auto-save! ✅

---

## 🎯 Khi nào dùng tool nào?

### **Dùng Gemini (MIỄN PHÍ) cho:**

✅ Câu hỏi thông thường: "What is X?"  
✅ Viết nội dung đơn giản  
✅ Dịch thuật  
✅ Tính toán cơ bản  
✅ Brainstorming  
✅ Dùng hàng ngày (1500 requests/day)

### **Dùng GPT-4 (TRẢ PHÍ) cho:**

✅ **Code generation phức tạp**  
✅ **Reasoning & logic tasks**  
✅ **Phân tích sâu**  
✅ **Writing chuyên nghiệp**  
✅ **Debug code**  
✅ **Khi Gemini không đủ tốt**

---

## 📊 Ví dụ cụ thể

### **Câu hỏi đơn giản:**

**Dùng Gemini (FREE):**
```
"What is Python?"
"Giải thích về AI"
"Dịch sang tiếng Anh: Xin chào"
```

### **Tasks phức tạp:**

**Dùng GPT-4 (PAID):**
```
"Write a complete Python web scraper with error handling"
"Debug this code and explain the issue: [paste code]"
"Create a professional business proposal for AI startup"
"Analyze this algorithm complexity: [paste code]"
```

---

## 🚀 Sử dụng

### **Via Dashboard:**

1. **Gemini:** Click "🤖 Hỏi Gemini AI" (màu tím)
2. **GPT-4:** Click "🧠 Hỏi GPT-4" (màu indigo/xanh đậm)

### **Via Xiaozhi AI:**

AI sẽ tự động chọn tool phù hợp dựa vào:
- Câu hỏi đơn giản → Gemini (miễn phí)
- Câu hỏi phức tạp → GPT-4 (khi có API key)

---

## 💡 Mẹo tiết kiệm chi phí

### **1. Dùng Gemini trước:**

Thử Gemini trước, chỉ dùng GPT-4 khi:
- Gemini không đủ tốt
- Cần reasoning phức tạp
- Cần code generation chuyên sâu

### **2. Giới hạn max_tokens:**

Code hiện tại: `max_tokens=1000`  
→ Giới hạn response ≤ 1000 tokens (~750 words)

### **3. Dùng gpt-4o thay vì gpt-4-turbo:**

- gpt-4o: $2.50/1M input (RẺ HƠN 4 LẦN)
- gpt-4-turbo: $10/1M input

---

## 📋 Config File

```json
{
  "endpoints": [...],
  "gemini_api_key": "AIzaSy...",
  "openai_api_key": "sk-proj-...",
  "last_updated": "..."
}
```

---

## 🎉 Tổng kết

**BÂY GIỜ BẠN CÓ 2 AI:**

🤖 **Gemini** - Miễn phí, nhanh, dùng hàng ngày  
🧠 **GPT-4** - Trả phí, mạnh nhất, dùng khi cần quality cao

**38 Tools total:** 36 công cụ cũ + Gemini + GPT-4

---

**📺 Dashboard: http://localhost:8000**  
**🎯 Test cả 2 AI và chọn cái phù hợp!** 🚀

