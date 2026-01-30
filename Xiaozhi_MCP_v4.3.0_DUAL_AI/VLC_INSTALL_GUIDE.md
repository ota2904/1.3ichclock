# 🎵 Hướng Dẫn Cài Đặt VLC Media Player

## Tại Sao Cần VLC?
miniZ MCP sử dụng VLC để phát nhạc từ thư mục `music_library/` trên máy tính của bạn.

## Cách 1: Cài Đặt VLC Bình Thường (Khuyến Nghị)

### Windows:
1. Tải VLC từ: https://www.videolan.org/vlc/
2. Click **"Download VLC"** (phiên bản Windows)
3. Chạy file `.exe` vừa tải về
4. Làm theo hướng dẫn cài đặt (Next → Next → Install)
5. ✅ Xong! miniZ sẽ tự động phát hiện VLC

### macOS:
1. Tải VLC từ: https://www.videolan.org/vlc/
2. Mở file `.dmg` vừa tải
3. Kéo VLC vào thư mục Applications
4. ✅ Xong!

### Linux:
```bash
# Ubuntu/Debian:
sudo apt install vlc python3-vlc

# Fedora:
sudo dnf install vlc python-vlc

# Arch Linux:
sudo pacman -S vlc python-vlc
```

## Cách 2: VLC Portable (Không Cần Cài Đặt)

### Windows Portable:
1. Tải VLC Portable: https://portableapps.com/apps/music_video/vlc_portable
2. Giải nén vào thư mục bất kỳ (ví dụ: `C:\VLC\`)
3. Chạy `VLCPortable.exe` một lần để khởi tạo
4. ✅ VLC đã sẵn sàng sử dụng!

**Lưu ý:** Với VLC Portable, bạn có thể copy toàn bộ thư mục sang máy khác mà không cần cài lại.

## Kiểm Tra VLC Đã Cài Đặt Thành Công

### Windows:
```powershell
# Mở PowerShell và chạy:
Get-Command vlc -ErrorAction SilentlyContinue
```
Nếu thấy đường dẫn đến `vlc.exe` → ✅ Thành công!

### macOS/Linux:
```bash
which vlc
```
Nếu thấy đường dẫn → ✅ Thành công!

## Cài Python VLC Bindings

Sau khi cài VLC, cần cài thư viện Python:

```bash
pip install python-vlc
```

Hoặc nếu đã có `requirements.txt`:
```bash
pip install -r requirements.txt
```

## Xử Lý Lỗi Thường Gặp

### ❌ "No module named 'vlc'"
**Giải pháp:**
```bash
pip install python-vlc
```

### ❌ "VLC Player not found"
**Giải pháp:**
- **Windows:** Thêm VLC vào PATH hoặc cài đặt lại VLC
- **macOS:** VLC phải ở trong `/Applications/VLC.app`
- **Linux:** `sudo apt install vlc`

### ❌ VLC phát nhạc nhưng không có âm thanh
**Giải pháp:**
1. Mở VLC Player thủ công
2. Vào: Tools → Preferences → Audio
3. Chọn đúng Output device (loa/tai nghe)
4. Click Save và restart miniZ

## Kiểm Tra miniZ Nhận Diện VLC

Sau khi cài VLC, khởi động miniZ:
```bash
python xiaozhi_final.py
```

Tìm dòng log:
```
✅ [VLC] VLC Music Player initialized (full UI mode)
```

Nếu thấy dòng này → ✅ VLC hoạt động tốt!

## Thêm Nhạc Vào Thư Viện

1. Copy file nhạc (MP3, FLAC, WAV, etc.) vào:
   ```
   music_library/Pop/
   music_library/Rock/
   music_library/Classical/
   ```

2. Reload Web UI hoặc gọi tool: `list_music`

3. ✅ Nhạc sẽ xuất hiện trong Music Player tab!

## Hỗ Trợ

Nếu gặp vấn đề, check:
- VLC đã cài đúng chưa?
- `python-vlc` đã cài chưa?
- File nhạc có trong `music_library/` chưa?
- Có lỗi gì trong console khi chạy `python xiaozhi_final.py`?

---
🎵 **Enjoy your music with miniZ MCP!**
