# 🌐 Quick Website Access Tools

## 📋 Danh Sách Công Cụ Mở Nhanh Website

Xiaozhi MCP Control Panel giờ đây có **5 công cụ** để mở nhanh các trang web phổ biến:

### 1️⃣ **open_youtube** - Mở YouTube
**Mô tả:** Mở YouTube trong browser với tùy chọn tìm kiếm

**Cách dùng:**
- `open_youtube()` → Mở trang chủ YouTube
- `open_youtube("nhạc Việt Nam")` → Tìm kiếm "nhạc Việt Nam" trên YouTube

**Ví dụ User:**
- "mở youtube"
- "mở youtube tìm kiếm nhạc Việt Nam"
- "xem youtube"

---

### 2️⃣ **open_facebook** - Mở Facebook
**Mô tả:** Mở Facebook trong browser

**Cách dùng:**
- `open_facebook()` → Mở trang chủ Facebook

**Ví dụ User:**
- "mở facebook"
- "vào facebook"
- "xem facebook"

---

### 3️⃣ **open_google** - Mở Google
**Mô tả:** Mở Google trong browser với tùy chọn tìm kiếm

**Cách dùng:**
- `open_google()` → Mở trang chủ Google
- `open_google("AI programming")` → Tìm kiếm "AI programming" trên Google

**Ví dụ User:**
- "mở google"
- "tìm kiếm AI programming trên google"
- "google search AI"

---

### 4️⃣ **open_tiktok** - Mở TikTok
**Mô tả:** Mở TikTok trong browser

**Cách dùng:**
- `open_tiktok()` → Mở trang chủ TikTok

**Ví dụ User:**
- "mở tiktok"
- "xem tiktok"
- "vào tiktok"

---

### 5️⃣ **open_website** - Mở Website Tùy Chỉnh
**Mô tả:** Mở bất kỳ trang web nào trong browser

**Cách dùng:**
- `open_website("github.com")` → Mở https://github.com
- `open_website("https://stackoverflow.com")` → Mở Stack Overflow

**Ví dụ User:**
- "mở github"
- "vào stackoverflow"
- "truy cập google.com"

---

## 🎯 Technical Details

### Browser Integration
- Sử dụng Python `webbrowser` module
- Mở trong browser mặc định của hệ thống
- Hỗ trợ tất cả browser hiện đại

### URL Handling
- **Auto HTTPS:** Tự động thêm `https://` nếu thiếu
- **Search Queries:** Chuyển đổi space thành `+` cho URL
- **Unicode Support:** Hỗ trợ tiếng Việt và ký tự đặc biệt

### Error Handling
- Trả về `{"success": false, "error": "..."}` nếu có lỗi
- Thông báo lỗi chi tiết cho debugging

---

## 📊 Test Results

```
✅ TEST 1: open_youtube() → YouTube homepage
✅ TEST 2: open_youtube("nhạc Việt Nam") → YouTube search
✅ TEST 3: open_facebook() → Facebook homepage
✅ TEST 4: open_google() → Google homepage
✅ TEST 5: open_google("AI programming") → Google search
✅ TEST 6: open_tiktok() → TikTok homepage
✅ TEST 7: open_website("github.com") → Auto HTTPS
✅ TEST 8: open_website("https://stackoverflow.com") → Full URL
```

---

## 🚀 Usage Examples

### Scenario 1: User wants to watch YouTube
```
User: "tôi muốn xem youtube"
AI: open_youtube()
Result: ✅ Browser opens YouTube homepage
```

### Scenario 2: User wants to search on YouTube
```
User: "tìm nhạc Việt Nam trên youtube"
AI: open_youtube("nhạc Việt Nam")
Result: ✅ Browser opens YouTube search results
```

### Scenario 3: User wants to check Facebook
```
User: "vào facebook xem tin nhắn"
AI: open_facebook()
Result: ✅ Browser opens Facebook
```

### Scenario 4: User wants to Google something
```
User: "tìm hiểu về AI programming"
AI: open_google("AI programming")
Result: ✅ Browser opens Google search results
```

### Scenario 5: User wants to browse TikTok
```
User: "xem tiktok trending"
AI: open_tiktok()
Result: ✅ Browser opens TikTok
```

### Scenario 6: User wants to visit a specific site
```
User: "mở github xem code"
AI: open_website("github.com")
Result: ✅ Browser opens GitHub
```

---

## 🔧 Implementation Notes

### Function Signatures
```python
async def open_youtube(search_query: str = "") -> dict
async def open_facebook() -> dict
async def open_google(search_query: str = "") -> dict
async def open_tiktok() -> dict
async def open_website(url: str) -> dict
```

### Response Format
```json
{
  "success": true,
  "message": "Đã mở YouTube với tìm kiếm: 'nhạc Việt Nam'",
  "url": "https://www.youtube.com/results?search_query=nhạc+Việt+Nam"
}
```

### Dependencies
- `webbrowser` (built-in Python module)
- Không cần cài đặt thêm gì

---

## 🎉 Benefits

1. **Quick Access:** Mở nhanh các trang web phổ biến
2. **Search Integration:** Tìm kiếm trực tiếp từ AI
3. **Vietnamese Support:** Hỗ trợ tiếng Việt hoàn hảo
4. **Flexible URLs:** Tự động xử lý URL với/ko HTTPS
5. **Error Handling:** Báo lỗi chi tiết khi có vấn đề
6. **Browser Agnostic:** Hoạt động với mọi browser

---

## 📝 Quick Reference

| Tool | Purpose | Search? | Example |
|------|---------|---------|---------|
| `open_youtube` | Watch videos | ✅ | "mở youtube tìm nhạc" |
| `open_facebook` | Social media | ❌ | "vào facebook" |
| `open_google` | Search web | ✅ | "google search AI" |
| `open_tiktok` | Short videos | ❌ | "xem tiktok" |
| `open_website` | Any website | ❌ | "mở github.com" |

**🎯 AI giờ có thể mở nhanh YouTube, Facebook, Google, TikTok và bất kỳ website nào!**