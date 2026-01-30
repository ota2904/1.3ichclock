# 🤖 Hướng Dẫn Sử Dụng Gemini AI

## 📋 Tổng quan

Xiaozhi MCP Control Panel đã được tích hợp **Google Gemini AI** - một mô hình ngôn ngữ lớn mạnh mẽ của Google. Bạn có thể hỏi đáp, phân tích, viết nội dung, giải thích code, và nhiều tác vụ AI khác thông qua MCP.

---

## 🚀 Cài đặt nhanh

### Bước 1: Lấy Gemini API Key

1. Truy cập: **https://aistudio.google.com/apikey**
2. Đăng nhập bằng tài khoản Google
3. Click **"Create API Key"** hoặc **"Get API key"**
4. Chọn project (hoặc tạo mới)
5. Copy API key (dạng: `AIzaSy...`)

**⚠️ Lưu ý:**
- API key là miễn phí với giới hạn quota
- Không chia sẻ API key với người khác
- Gemini API hỗ trợ 1500 requests/day (free tier)

---

### Bước 2: Cấu hình API Key

#### **Cách 1: Qua file JSON (Khuyến nghị)**

Mở file `xiaozhi_endpoints.json` và thêm API key:

```json
{
  "endpoints": [
    {
      "name": "Thiết bị 1",
      "token": "your-xiaozhi-token...",
      "enabled": true
    }
  ],
  "active_index": 0,
  "gemini_api_key": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "last_updated": "2025-11-06T..."
}
```

**Lưu ý:** Thay `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXX` bằng API key thật của bạn.

#### **Cách 2: Auto-reload khi khởi động**

Server tự động load API key từ file khi khởi động. Nếu thấy dòng này là thành công:

```
✅ [Gemini] API key loaded (ends with ...XXXXXXXX)
```

---

### Bước 3: Cài đặt thư viện (nếu chưa có)

```bash
pip install google-generativeai
```

Hoặc chạy lại:

```bash
pip install -r requirements.txt
```

---

## 🎯 Sử dụng

### Qua AI (Xiaozhi)

Sau khi kết nối MCP, bạn có thể hỏi AI:

**Ví dụ:**
- "Hỏi Gemini: What is the meaning of life?"
- "Dùng Gemini phân tích đoạn code này"
- "Yêu cầu Gemini viết email chuyên nghiệp"
- "Hỏi Gemini giải thích về quantum computing"

AI sẽ tự động gọi tool `ask_gemini()` và trả về câu trả lời.

---

### Qua Dashboard Web

1. Mở http://localhost:8000
2. Vào tab **"🛠️ Công Cụ"**
3. Tìm section **"Gemini AI"**
4. Nhập câu hỏi vào ô "Prompt"
5. (Tùy chọn) Chọn model: `gemini-2.0-flash-exp`, `gemini-1.5-pro`, hoặc `gemini-1.5-flash`
6. Click **"Gửi"**

---

## 📊 Models có sẵn

| Model | Tốc độ | Chất lượng | Use Case |
|-------|--------|------------|----------|
| `gemini-2.5-flash` | ⚡⚡⚡⚡ Siêu nhanh | ⭐⭐⭐⭐ Rất tốt | **Mặc định** - Model Flash 2.5 mới nhất |
| `gemini-2.5-pro` | ⚡⚡ Nhanh | ⭐⭐⭐⭐⭐ Xuất sắc | Chất lượng cao nhất, phân tích phức tạp |
| `gemini-2.0-flash-exp` | ⚡⚡⚡ Rất nhanh | ⭐⭐⭐ Tốt | Flash 2.0 - phiên bản cũ hơn |
| `gemini-1.5-pro` | ⚡ Chậm | ⭐⭐⭐⭐ Rất tốt | Ổn định, phân tích sâu |
| `gemini-1.5-flash` | ⚡⚡⚡ Rất nhanh | ⭐⭐⭐ Tốt | Chat đơn giản, hỏi đáp nhanh |

**Khuyến nghị:**
- Dùng `gemini-2.5-flash` cho hầu hết các trường hợp (mặc định) - Mới nhất & nhanh nhất
- Dùng `gemini-2.5-pro` khi cần câu trả lời chi tiết nhất, phân tích phức tạp
- Dùng `gemini-1.5-pro` khi cần sự ổn định và phân tích sâu

---

## 💡 Use Cases

### 1️⃣ Viết nội dung

**Prompt:**
```
Viết một email chuyên nghiệp để xin nghỉ phép 2 ngày vì lý do gia đình.
```

### 2️⃣ Phân tích code

**Prompt:**
```
Giải thích đoạn code Python này làm gì:

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 3️⃣ Dịch thuật

**Prompt:**
```
Dịch sang tiếng Anh: "Tôi đang học lập trình để trở thành developer giỏi."
```

### 4️⃣ Giải toán

**Prompt:**
```
Giải phương trình: 2x^2 + 5x - 3 = 0
```

### 5️⃣ Brainstorming

**Prompt:**
```
Cho tôi 10 ý tưởng tên cho một startup về AI education.
```

### 6️⃣ Tóm tắt văn bản

**Prompt:**
```
Tóm tắt bài viết này trong 3 câu: [paste long text]
```

---

## 🔧 API Response Format

Tool `ask_gemini()` trả về JSON với cấu trúc:

```json
{
  "success": true,
  "prompt": "What is the meaning of life?",
  "response_text": "The meaning of life is a philosophical question...",
  "model": "gemini-2.5-flash",
  "message": "✅ Gemini đã trả lời (model: gemini-2.5-flash)"
}
```

**Fields:**
- `success`: `true` nếu thành công, `false` nếu có lỗi
- `prompt`: Câu hỏi bạn đã gửi
- `response_text`: Câu trả lời từ Gemini
- `model`: Model đã sử dụng
- `message`: Thông báo status

---

## ⚠️ Xử lý lỗi

### Lỗi 1: API key chưa cấu hình

**Lỗi:**
```json
{
  "success": false,
  "error": "Gemini API key chưa được cấu hình. Vui lòng thêm 'gemini_api_key' vào xiaozhi_endpoints.json",
  "help": "Lấy API key tại: https://aistudio.google.com/apikey"
}
```

**Giải pháp:** Thêm API key vào `xiaozhi_endpoints.json` như hướng dẫn ở **Bước 2**.

---

### Lỗi 2: API key không hợp lệ

**Lỗi:**
```json
{
  "success": false,
  "error": "API key không hợp lệ. Vui lòng kiểm tra lại gemini_api_key trong xiaozhi_endpoints.json",
  "help": "Lấy API key mới tại: https://aistudio.google.com/apikey"
}
```

**Giải pháp:**
1. Kiểm tra API key có đúng không (copy lại từ Google AI Studio)
2. Đảm bảo không có khoảng trắng thừa
3. Tạo API key mới nếu cũ đã expire

---

### Lỗi 3: Vượt quota

**Lỗi:**
```json
{
  "success": false,
  "error": "Đã vượt quá quota API. Vui lòng chờ hoặc nâng cấp plan.",
  "details": "Resource has been exhausted..."
}
```

**Giải pháp:**
1. Chờ đến ngày hôm sau (quota reset hàng ngày)
2. Nâng cấp lên paid plan tại: https://ai.google.dev/pricing
3. Sử dụng API key khác

---

### Lỗi 4: Rate limit

**Lỗi:**
```json
{
  "success": false,
  "error": "Rate limit exceeded. Vui lòng thử lại sau ít phút.",
  "details": "Too many requests..."
}
```

**Giải pháp:**
1. Chờ 1-2 phút rồi thử lại
2. Giảm số lượng requests/phút

---

### Lỗi 5: Library chưa cài

**Lỗi:**
```json
{
  "success": false,
  "error": "Gemini library chưa cài đặt. Chạy: pip install google-generativeai"
}
```

**Giải pháp:**
```bash
pip install google-generativeai
```

---

## 📈 Quota & Pricing (Free Tier)

**Gemini API Free Tier:**
- ✅ **1,500 requests/day** (RPD)
- ✅ **15 RPM** (requests per minute)
- ✅ **1 million tokens/minute** (TPM)
- ✅ **Miễn phí vĩnh viễn**

**Paid Plan:** (nếu cần nhiều hơn)
- 💰 Pay-as-you-go pricing
- 📊 Xem: https://ai.google.dev/pricing

---

## 🔐 Bảo mật

### ✅ Best Practices

1. **Không commit API key lên GitHub**
   - Thêm `xiaozhi_endpoints.json` vào `.gitignore`
   - Không chia sẻ API key công khai

2. **Rotate API key định kỳ**
   - Tạo API key mới mỗi 3-6 tháng
   - Xóa key cũ sau khi thay thế

3. **Giới hạn quyền API key**
   - Chỉ enable Gemini API trên Google Cloud Console
   - Disable các API khác không dùng

4. **Monitor usage**
   - Kiểm tra quota usage tại: https://aistudio.google.com/apikey
   - Set up alerts khi gần hết quota

---

## 🐛 Troubleshooting

### Server không nhận API key?

```bash
# Restart server sau khi thêm API key
python xiaozhi_final.py
```

Xem log console, phải thấy dòng:
```
✅ [Gemini] API key loaded (ends with ...XXXXXXXX)
```

---

### Tool không xuất hiện trong dashboard?

1. Kiểm tra file `xiaozhi_final.py` đã có tool `ask_gemini` trong TOOLS dictionary
2. Clear browser cache (Ctrl + F5)
3. Restart server

---

### Response quá chậm?

1. Model mặc định `gemini-2.5-flash` đã là nhanh nhất trong dòng 2.5
2. Nếu vẫn chậm, kiểm tra kết nối internet
3. Rút ngắn prompt nếu prompt quá dài

---

## 📝 Examples

### Example 1: Hỏi đáp đơn giản

**Request:**
```json
{
  "tool": "ask_gemini",
  "prompt": "What is Python?"
}
```

**Response:**
```json
{
  "success": true,
  "response_text": "Python is a high-level, interpreted programming language known for its readability and versatility...",
  "model": "gemini-2.0-flash-exp"
}
```

---

### Example 2: Chọn model cụ thể

**Request:**
```json
{
  "tool": "ask_gemini",
  "prompt": "Explain quantum entanglement in detail",
  "model": "gemini-1.5-pro"
}
```

**Response:**
```json
{
  "success": true,
  "response_text": "Quantum entanglement is a physical phenomenon that occurs when pairs or groups of particles...",
  "model": "gemini-1.5-pro"
}
```

---

## 🎉 Kết luận

**Bạn đã sẵn sàng sử dụng Gemini AI!**

Với tính năng này, Xiaozhi MCP Control Panel trở thành một trợ lý AI toàn diện, có thể:
- ✅ Điều khiển máy tính (35+ tools)
- ✅ Hỏi đáp với Gemini AI
- ✅ Tích hợp đa dạng dịch vụ (VnExpress, GiaVang, YouTube, etc.)

---

## 📞 Hỗ trợ

- **Gemini API Docs**: https://ai.google.dev/docs
- **API Key**: https://aistudio.google.com/apikey
- **Pricing**: https://ai.google.dev/pricing
- **YouTube miniZ**: [https://youtube.com/@minizjp](https://youtube.com/@minizjp?si=LRg5piGHmxYtsFJU)

---

**Made with ❤️ for Xiaozhi MCP + Google Gemini AI**

