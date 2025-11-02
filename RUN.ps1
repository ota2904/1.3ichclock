# Xiaozhi Ultimate - 1 Click Launcher
# Khởi động tất cả chỉ bằng 1 lệnh!

$Host.UI.RawUI.WindowTitle = "Xiaozhi Ultimate Server"
$Host.UI.RawUI.ForegroundColor = "Green"

Clear-Host
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   🚀 XIAOZHI ULTIMATE SERVER" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   ✨ All-in-One: Web UI + WebSocket MCP + Dashboard" -ForegroundColor Green
Write-Host "   🌐 URL: http://localhost:8000" -ForegroundColor White
Write-Host "   📡 Xiaozhi MCP: Auto-connect" -ForegroundColor White
Write-Host "   🛑 Nhấn Ctrl+C để dừng" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Đang khởi động server..." -ForegroundColor White
Write-Host ""

# Wait 2 seconds then open browser
Start-Sleep -Seconds 3
Start-Process "http://localhost:8000"

# Run server
python xiaozhi_ultimate.py

Write-Host ""
Write-Host "   Server đã dừng." -ForegroundColor Yellow
Write-Host ""
Read-Host "Nhấn Enter để thoát"
