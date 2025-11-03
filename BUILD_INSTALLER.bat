@echo off
chcp 65001 >nul
echo.
echo ═══════════════════════════════════════════════════════════
echo   🏗️  XIAOZHI MCP INSTALLER BUILDER
echo ═══════════════════════════════════════════════════════════
echo.
echo 📦 Script này sẽ tạo file .exe standalone cho Xiaozhi MCP
echo ⏱️  Thời gian build: ~5-10 phút
echo 💾 Kích thước file .exe: ~50-100 MB
echo.
echo ═══════════════════════════════════════════════════════════
echo.

pause

echo.
echo 🚀 Bắt đầu build...
echo.

python build_installer.py

echo.
echo ═══════════════════════════════════════════════════════════
echo   ✅ BUILD HOÀN TẤT!
echo ═══════════════════════════════════════════════════════════
echo.
echo 📂 File installer: Xiaozhi_MCP_Release\XiaozhiMCP.exe
echo 📖 Xem hướng dẫn: Xiaozhi_MCP_Release\SETUP_GUIDE.txt
echo.
echo 💡 Bạn có thể:
echo    1. Copy folder Xiaozhi_MCP_Release giao cho khách hàng
echo    2. Chạy XiaozhiMCP.exe để test thử
echo    3. Không cần cài Python hay dependencies!
echo.
echo ═══════════════════════════════════════════════════════════
echo.

pause
