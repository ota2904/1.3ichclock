# 📰 Hướng Dẫn Lấy Thông Tin Mới (Real-time)

## ⚠️ Giới hạn của Gemini AI

**Gemini chỉ biết đến tháng 10/2024**

Gemini KHÔNG thể trả lời về:
- ❌ Sự kiện sau 10/2024
- ❌ Tin tức hôm nay
- ❌ Kết quả thi đấu mới nhất
- ❌ Giá cả hiện tại
- ❌ Thông tin real-time

**Ví dụ:**
- ❌ "Ai là nhà vô địch Olympia 2025?" → Gemini không biết
- ❌ "Giá vàng hôm nay?" → Gemini không biết
- ❌ "Tin tức mới nhất?" → Gemini không biết

---

## ✅ Giải pháp: Dùng các tools REAL-TIME

### **1. 🔍 search_web - Mở browser Google**

**Khi nào dùng:**
- Cần TÌM KIẾM thông tin mới
- Muốn XEM kết quả trên browser
- Cần ĐỌC chi tiết từ nhiều nguồn

**Cách dùng:**

Nói với Xiaozhi:
```
"Mở Google tìm kiếm nhà vô địch olympia 2025"
"Search Google về world cup 2025"
"Tìm kiếm tin tức olympia vietnam"
```

**Kết quả:**
- ✅ Mở browser với kết quả Google
- ✅ Bạn đọc và chọn nguồn tin
- ✅ Thông tin REAL-TIME (mới nhất)

---

### **2. 📰 get_vnexpress_news - Tin tức VnExpress**

**Khi nào dùng:**
- Cần tin tức VIỆT NAM
- Tin tức theo CHỦ ĐỀ
- Nguồn tin UY TÍN

**Cách dùng:**

Nói với Xiaozhi:
```
"Cho tôi tin tức giáo dục mới nhất"
"Tin tức thể thao hôm nay"
"Tin tức về Olympia"
```

**Categories có sẵn:**
- `giao-duc` - Giáo dục (có thể có tin về Olympia)
- `the-thao` - Thể thao
- `home` - Mới nhất
- `thoi-su` - Thời sự
- `the-gioi` - Thế giới
- Và nhiều hơn...

**Kết quả:**
```json
{
  "success": true,
  "articles": [
    {
      "title": "Chung kết Olympia 2025...",
      "link": "https://vnexpress.net/...",
      "description": "...",
      "pubDate": "2025-11-06"
    }
  ]
}
```

---

### **3. 💰 get_gold_price - Giá vàng real-time**

**Khi nào dùng:**
- Cần giá vàng HÔM NAY
- Cập nhật REAL-TIME từ GiaVang.org

**Cách dùng:**

Nói với Xiaozhi:
```
"Giá vàng hôm nay"
"Cho tôi biết giá vàng SJC"
```

**Kết quả:**
- ✅ Giá vàng từ nhiều nguồn (SJC, DOJI, PNJ...)
- ✅ Cập nhật real-time
- ✅ Giá mua vào và bán ra

---

## 🎯 Workflow Kết Hợp: Gemini + Real-time Tools

### **Kịch bản 1: Olympia 2025**

**Bước 1: Lấy thông tin mới**
```
User: "Tìm tin về nhà vô địch Olympia 2025 trên VnExpress"
AI → get_vnexpress_news(category="giao-duc")
→ Trả về tin tức mới nhất
```

**Bước 2: Phân tích với Gemini**
```
User: "Gemini hãy tóm tắt tin này: [paste nội dung tin]"
AI → ask_gemini(prompt="Tóm tắt: ...")
→ Gemini tóm tắt nội dung
```

---

### **Kịch bản 2: Thông tin nhanh**

**Option A: Mở browser (nhanh nhất)**
```
User: "Mở Google tìm olympia 2025"
AI → search_web("olympia 2025")
→ Browser mở với kết quả
→ User tự đọc
```

**Option B: Qua tin tức**
```
User: "Tin tức giáo dục mới nhất"
AI → get_vnexpress_news(category="giao-duc")
→ Danh sách tin + links
→ User click link để đọc
```

---

## 📊 So sánh các phương án

### **Cho câu hỏi: "Ai là nhà vô địch Olympia 2025?"**

| Phương án | Tool | Kết quả | Ưu điểm | Nhược điểm |
|-----------|------|---------|---------|------------|
| **1. Gemini** | `ask_gemini` | ❌ "Chưa biết" | Nhanh | Không có data mới |
| **2. Search Web** | `search_web` | ✅ Mở browser | Mới nhất | Phải đọc thủ công |
| **3. VnExpress** | `get_vnexpress_news` | ✅ Tin RSS | Nguồn uy tín | Chỉ có tin Việt |

**KHUYẾN NGHỊ:**

Dùng **VnExpress** cho tin Việt Nam:
```
"Cho tôi tin giáo dục mới nhất"
```

Hoặc **Search Web** cho search tổng quát:
```
"Mở Google tìm olympia 2025"
```

---

## 💡 Mẹo sử dụng

### **Mẹo 1: Kết hợp 2 tools**

```
Bước 1: "Tin giáo dục mới nhất" → Lấy links
Bước 2: Mở link trong browser
Bước 3: Copy nội dung
Bước 4: "Gemini tóm tắt: [paste]" → Gemini phân tích
```

### **Mẹo 2: Hỏi đúng tool**

**Thông tin CŨ (trước 10/2024):**
```
✅ "What is Python?" → ask_gemini
✅ "Giải thích về AI" → ask_gemini
✅ "Lịch sử Olympia" → ask_gemini
```

**Thông tin MỚI (sau 10/2024):**
```
✅ "Olympia 2025 winner" → search_web hoặc get_vnexpress_news
✅ "Giá vàng hôm nay" → get_gold_price
✅ "Tin tức mới nhất" → get_vnexpress_news
```

---

## 🎯 Ví dụ thực tế

### **Câu hỏi của bạn:**

```
"ai là nhà vô địch đường lên đỉnh olympia 2025"
```

**Giải pháp tốt nhất:**

**Cách 1: VnExpress (Khuyến nghị)**
```
User: "Cho tôi tin giáo dục mới nhất"
AI → get_vnexpress_news(category="giao-duc")
→ Danh sách tin, có thể có tin về Olympia
```

**Cách 2: Search Web**
```
User: "Mở Google tìm nhà vô địch olympia 2025"
AI → search_web("nhà vô địch olympia 2025")
→ Browser mở với kết quả
```

**Cách 3: VnExpress + Gemini**
```
Bước 1: "Tin giáo dục" → Lấy tin
Bước 2: Đọc tin tìm thông tin olympia
Bước 3: Copy nội dung
Bước 4: "Gemini tóm tắt tin này: [paste]"
```

---

## 📋 Tools cho thông tin Real-Time

| Tool | Type | Use Case | Example |
|------|------|----------|---------|
| `search_web` | Browser | Search tổng quát | "Mở Google tìm X" |
| `get_vnexpress_news` | RSS | Tin Việt Nam | "Tin giáo dục mới nhất" |
| `get_gold_price` | Scraping | Giá vàng | "Giá vàng hôm nay" |
| `get_network_info` | System | Thông tin mạng | "IP của tôi" |
| `get_battery_status` | System | Pin laptop | "Pin còn bao nhiêu" |

---

## 🎉 Kết luận

**Cho thông tin REAL-TIME:**
- ✅ Dùng `search_web` (mở browser)
- ✅ Dùng `get_vnexpress_news` (tin Việt)
- ✅ Dùng `get_gold_price` (giá vàng)

**Cho câu hỏi CHUNG:**
- ✅ Dùng `ask_gemini` (AI trả lời)

**Kết hợp:**
- ✅ Search → Lấy info → Gemini phân tích

---

**📺 Server đang chạy: http://localhost:8000**  
**🎯 Bây giờ bạn có 37 tools (36 + 1 search_google_text)!**

---

🎉 **Gemini + Real-time Tools = Trợ lý hoàn hảo!** 🚀

