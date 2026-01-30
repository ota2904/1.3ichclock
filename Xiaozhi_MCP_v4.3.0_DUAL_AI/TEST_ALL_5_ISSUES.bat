@echo off
chcp 65001 > nul
echo.
echo ================================================================
echo 🧪 KIỂM TRA TOÀN BỘ 5 VẤN ĐỀ
echo ================================================================
echo.
echo This test will check:
echo   1. API keys hardcoded trong source
echo   2. Chức năng lưu config/endpoints
echo   3. Mở trực tiếp video YouTube (không chỉ search)
echo   4. Lưu và kích hoạt JWT Token/Endpoint  
echo   5. Mở nhạc từ thư mục người dùng
echo.
echo ⚠️  Đảm bảo server đã chạy: python xiaozhi_final.py
echo.
pause
echo.

python test_all_5_issues.py

echo.
echo ================================================================
echo 💡 NẾU CÓ LỖI:
echo ================================================================
echo.
echo 1. API keys hardcode:
echo    → OK nếu lưu trong xiaozhi_endpoints.json
echo.
echo 2. Lưu config không hoạt động:
echo    → Kiểm tra quyền write file
echo    → Xem xiaozhi_endpoints.json có được tạo không
echo.
echo 3. YouTube không mở trực tiếp video:
echo    → Cài: pip install youtube-search-python
echo    → Kiểm tra search_youtube_video function
echo.
echo 4. JWT Token không lưu:
echo    → Kiểm tra /api/save_endpoints API
echo    → Xem token trong xiaozhi_endpoints.json
echo.
echo 5. Music folder không hoạt động:
echo    → Tạo custom_music_folder.txt với đường dẫn
echo    → Hoặc dùng music_library/ mặc định
echo.
pause
