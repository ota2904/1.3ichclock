@echo off
chcp 65001 > nul
echo.
echo ================================================================
echo 🧪 TEST YOUTUBE DIRECT VIDEO FIX
echo ================================================================
echo.
echo This will test the new YouTube direct video feature:
echo   - Query with 3+ words → Direct video
echo   - Query with 1-2 words → Search page
echo   - No query → Homepage
echo.
echo ⚠️  Make sure server is running: python xiaozhi_final.py
echo ⚠️  Install dependency: pip install youtube-search-python
echo.
pause
echo.

python test_youtube_direct_fix.py

echo.
echo ================================================================
echo 💡 ABOUT THE FIX
echo ================================================================
echo.
echo BEFORE:
echo   open_youtube("Sơn Tùng Chúng Ta") 
echo   → Opens: youtube.com/results?search_query=...
echo.
echo AFTER:
echo   open_youtube("Sơn Tùng Chúng Ta Của Hiện Tại")
echo   → Opens: youtube.com/watch?v=VIDEO_ID (direct video!)
echo.
echo The fix auto-detects:
echo   - Specific queries (3+ words) → Direct video
echo   - General queries (1-2 words) → Search page
echo.
pause
