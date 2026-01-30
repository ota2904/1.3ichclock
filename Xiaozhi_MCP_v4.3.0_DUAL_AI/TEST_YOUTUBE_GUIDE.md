# 🧪 HƯỚNG DẪN TEST YOUTUBE AUTO-DETECT

## ✅ Code đã được cập nhật

**Threshold mới:** `>= 2 từ` (thay vì >= 3 từ)

**3 vị trí đã update:**
1. ✅ `open_youtube()` function - Logic code
2. ✅ Tool description trong registry
3. ✅ System prompt cho LLM

---

## 🚀 CÁCH TEST

### Option 1: Test qua Web UI (RECOMMENDED)

1. **Khởi động server:**
   ```bash
   python xiaozhi_final.py
   ```

2. **Mở browser:** http://localhost:8000

3. **Test bằng voice hoặc chat:**
   - 🎤 Nói: "mở youtube Lạc Trôi"
   - 💬 Chat: "mở youtube Lạc Trôi"
   - 🎤 Nói: "mở youtube Sơn Tùng MTP"

4. **Kết quả mong đợi:**
   - ✅ Video sẽ mở trực tiếp (youtube.com/watch?v=...)
   - ✅ KHÔNG phải search page

---

### Option 2: Test qua Python script

```bash
# Khởi động server trước
python xiaozhi_final.py

# Terminal mới, chạy test
python test_server_youtube.py
```

---

### Option 3: Test logic (không cần server)

```bash
python test_youtube_2_words.py
```

**Kết quả:**
```
✅ 'Lạc Trôi' (2 từ) → Direct video
✅ 'Sơn Tùng MTP' (3 từ) → Direct video
✅ 'Chúng Ta Của Hiện Tại' (5 từ) → Direct video
⚠️  'nhạc' (1 từ) → Search page
🏠 '' (0 từ) → Homepage
```

---

## 📋 TEST CASES

| Query | Số từ | Expected Mode | URL Type |
|-------|-------|---------------|----------|
| "Lạc Trôi" | 2 | direct_video | youtube.com/watch?v=... |
| "Sơn Tùng MTP" | 3 | direct_video | youtube.com/watch?v=... |
| "nhạc buồn" | 2 | direct_video | youtube.com/watch?v=... |
| "nhạc" | 1 | search_page | youtube.com/results?... |
| "" | 0 | homepage | youtube.com |

---

## ✅ VERIFICATION

Sau khi test, verify:

1. **"Lạc Trôi" mở video trực tiếp:**
   - ✅ URL dạng: `https://www.youtube.com/watch?v=DrY_K0mT-As`
   - ✅ Video phát ngay
   - ❌ KHÔNG phải: `https://www.youtube.com/results?search_query=...`

2. **"nhạc" vẫn mở search page:**
   - ✅ URL dạng: `https://www.youtube.com/results?search_query=nh%E1%BA%A1c`
   - ✅ Trang search

3. **Check console log:**
   - ✅ `[YouTube] Detecting specific video query: 'Lạc Trôi'`
   - ✅ `[YouTube] Opened direct video: ...`

---

## 🔧 NẾU CÓ VẤN ĐỀ

### Issue 1: Vẫn ra search page
**Nguyên nhân:** Cache hoặc code chưa reload
**Fix:** 
1. Tắt server (Ctrl+C)
2. Xóa cache: `Remove-Item __pycache__ -Recurse -Force`
3. Restart: `python xiaozhi_final.py`

### Issue 2: LLM không gọi tool
**Nguyên nhân:** Conversation history cũ
**Fix:**
1. Clear conversation trong UI
2. Hoặc xóa: `C:\Users\<username>\AppData\Local\miniZ_MCP\conversations\`

### Issue 3: API không response
**Nguyên nhân:** Server chưa khởi động
**Fix:** Check http://localhost:8000 có mở được không

---

## 📊 EXPECTED RESULTS

**✅ PASS nếu:**
- "Lạc Trôi" → Video trực tiếp mở
- "Sơn Tùng MTP" → Video trực tiếp mở
- "nhạc" → Search page mở
- Console log hiển thị "Detecting specific video query"

**❌ FAIL nếu:**
- "Lạc Trôi" → Vẫn ra search page
- URL có dạng `/results?search_query=` thay vì `/watch?v=`

---

## 🎯 NEXT STEPS

Sau khi test PASS:
1. Build EXE mới với threshold >= 2 words
2. Distribute EXE cho users
3. Update documentation

**Build command:**
```bash
python -m PyInstaller --clean --noconfirm --distpath "dist_new" --workpath "build_new" "miniZ_MCP_v4.3.1_FINAL.spec"
```
