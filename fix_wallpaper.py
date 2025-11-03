import re

with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Sửa change_wallpaper
old_pattern = r'async def change_wallpaper\(keyword: str = ""\) -> dict:\s+"""Đổi hình nền desktop \(từ API\)"""[\s\S]+?except Exception as e:\s+return \{"success": False, "error": str\(e\)\}'

new_function = """async def change_wallpaper(keyword: str = "") -> dict:
    \"\"\"Đổi hình nền desktop (dùng hình Windows có sẵn)\"\"\"
    try:
        import ctypes
        import os
        import random

        # Đường dẫn hình nền Windows mặc định
        wallpaper_paths = [
            r"C:\\Windows\\Web\\Wallpaper\\Windows\\img0.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Windows\\img19.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Flower\\img0.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Flower\\img1.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Nature\\img0.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Nature\\img1.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Nature\\img2.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Architecture\\img0.jpg",
            r"C:\\Windows\\Web\\Wallpaper\\Characters\\img0.jpg",
        ]

        # Lọc các file tồn tại
        available = [p for p in wallpaper_paths if os.path.exists(p)]
        
        if not available:
            return {"success": False, "error": "Không tìm thấy hình nền Windows"}

        # Chọn ngẫu nhiên
        selected = random.choice(available)
        
        # Đặt hình nền
        ctypes.windll.user32.SystemParametersInfoW(0x0014, 0, selected, 0x01 | 0x02)
        
        filename = os.path.basename(selected)
        return {"success": True, "message": f"Đã đổi hình nền: {filename}"}
    except Exception as e:
        return {"success": False, "error": str(e)}"""

content = re.sub(old_pattern, new_function, content, count=1)

# 2. Thêm auto-open browser
old_main = '''if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print(" XIAOZHI FINAL - SIDEBAR UI")
    print("=" * 60)
    print(" Web Dashboard: http://localhost:8000")
    print(" WebSocket MCP: Multi-device support")
    print("  Tools: 30 available (20 original + 10 new from reference)")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)'''

new_main = '''if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    
    def open_browser():
        """Mở browser sau 2 giây"""
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
    
    # Khởi động thread mở browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    print("=" * 60)
    print(" XIAOZHI FINAL - SIDEBAR UI")
    print("=" * 60)
    print(" Web Dashboard: http://localhost:8000")
    print(" WebSocket MCP: Multi-device support")
    print("  Tools: 30 available (20 original + 10 new from reference)")
    print(" Browser sẽ tự động mở sau 2 giây...")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)'''

content = content.replace(old_main, new_main)

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print(" Đã sửa xong!")
print("   1. change_wallpaper  Dùng hình Windows có sẵn (9 hình)")
print("   2. Auto-open browser sau 2 giây")
