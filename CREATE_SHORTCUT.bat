@echo off
:: Tạo shortcut trên Desktop để dễ dàng khởi động
echo Đang tạo shortcut trên Desktop...

set SCRIPT_DIR=%~dp0
set TARGET=%SCRIPT_DIR%START.bat
set SHORTCUT=%USERPROFILE%\Desktop\Xiaozhi MCP.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%TARGET%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.IconLocation = 'shell32.dll,13'; $s.Description = 'Xiaozhi MCP Control Panel'; $s.Save()"

if exist "%SHORTCUT%" (
    echo ✅ Đã tạo shortcut: Desktop\Xiaozhi MCP.lnk
    echo    → Double-click để khởi động nhanh!
) else (
    echo ❌ Lỗi khi tạo shortcut
)

pause
