"""
miniZ MCP System Tray Application
Chạy ngầm trong system tray với menu context
"""

import os
import sys
import threading
import webbrowser
import argparse
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Check for tray support
try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("⚠️ pystray hoặc PIL chưa cài đặt. System tray sẽ không hoạt động.")
    print("   Cài đặt: pip install pystray Pillow")

# Import startup manager
try:
    from startup_manager import enable_startup, disable_startup, is_startup_enabled
    STARTUP_AVAILABLE = True
except ImportError:
    STARTUP_AVAILABLE = False
    print("⚠️ startup_manager.py không tìm thấy")

APP_NAME = "miniZ MCP"
APP_VERSION = "4.3.0"
APP_PORT = 8000
DASHBOARD_URL = f"http://localhost:{APP_PORT}"

def create_icon_image(size=64):
    """Create a gradient icon for system tray"""
    width = size
    height = size
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw gradient circle
    for y in range(height):
        for x in range(width):
            # Check if inside circle
            cx, cy = width // 2, height // 2
            radius = min(width, height) // 2 - 2
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            
            if dist <= radius:
                # Gradient from #667eea to #764ba2
                ratio = y / height
                r = int(102 + (118 - 102) * ratio)
                g = int(126 + (75 - 126) * ratio)
                b = int(234 + (162 - 234) * ratio)
                
                # Anti-aliasing at edges
                if dist > radius - 1:
                    alpha = int(255 * (radius - dist + 1))
                else:
                    alpha = 255
                
                draw.point((x, y), fill=(r, g, b, alpha))
    
    # Draw "MZ" text
    try:
        font = ImageFont.truetype("arial.ttf", size // 3)
    except:
        font = ImageFont.load_default()
    
    text = "MZ"
    # Get text bounding box
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # Fallback for older PIL versions
        text_width, text_height = draw.textsize(text, font=font)
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2 - 2
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    return image

def open_dashboard(icon=None, item=None):
    """Open web dashboard in browser"""
    print(f"🌐 Opening dashboard: {DASHBOARD_URL}")
    webbrowser.open(DASHBOARD_URL)

def toggle_startup_menu(icon, item):
    """Toggle startup setting from menu"""
    if not STARTUP_AVAILABLE:
        icon.notify("Startup manager không khả dụng", APP_NAME)
        return
    
    if is_startup_enabled():
        if disable_startup():
            icon.notify("Đã tắt khởi động cùng Windows", APP_NAME)
    else:
        exe_path = sys.executable
        if enable_startup(exe_path, run_hidden=True):
            icon.notify("Đã bật khởi động cùng Windows", APP_NAME)

def show_about(icon, item):
    """Show about dialog"""
    icon.notify(
        f"Version {APP_VERSION}\n"
        f"Điều khiển máy tính bằng AI\n"
        f"Dashboard: {DASHBOARD_URL}",
        APP_NAME
    )

def exit_app(icon, item):
    """Exit application"""
    print("👋 Exiting miniZ MCP...")
    icon.stop()
    # Give time for cleanup
    import time
    time.sleep(0.5)
    os._exit(0)

def run_server():
    """Run the main server"""
    print(f"\n{'='*50}")
    print(f"  🚀 miniZ MCP Server v{APP_VERSION}")
    print(f"  🌐 Dashboard: {DASHBOARD_URL}")
    print(f"{'='*50}\n")
    
    # Import and run the main server
    try:
        # Change to the correct directory
        os.chdir(str(BASE_DIR))
        
        # Import the main module
        import xiaozhi_final
        
        # Run uvicorn server (the code in if __name__ == "__main__" won't run when imported)
        import uvicorn
        print("🚀 Starting FastAPI server...")
        
        # Check if frozen (running as EXE)
        if getattr(sys, 'frozen', False):
            # Disable uvicorn's default logging config when frozen
            uvicorn.run(xiaozhi_final.app, host="0.0.0.0", port=APP_PORT, log_config=None)
        else:
            uvicorn.run(xiaozhi_final.app, host="0.0.0.0", port=APP_PORT)
        
    except ImportError as e:
        print(f"❌ Error importing xiaozhi_final: {e}")
        print("   Make sure xiaozhi_final.py is in the same directory")
    except Exception as e:
        print(f"❌ Error running server: {e}")
        import traceback
        traceback.print_exc()

def run_with_tray():
    """Run with system tray icon"""
    if not TRAY_AVAILABLE:
        print("❌ System tray không khả dụng. Chạy ở chế độ foreground...")
        run_server()
        return
    
    print("🎯 Starting miniZ MCP with system tray...")
    
    # Build menu
    menu_items = [
        pystray.MenuItem("🌐 Mở Dashboard", open_dashboard, default=True),
        pystray.Menu.SEPARATOR,
    ]
    
    # Add startup toggle if available
    if STARTUP_AVAILABLE:
        menu_items.append(
            pystray.MenuItem(
                "🚀 Khởi động cùng Windows",
                toggle_startup_menu,
                checked=lambda item: is_startup_enabled() if STARTUP_AVAILABLE else False
            )
        )
    
    menu_items.extend([
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("ℹ️ About", show_about),
        pystray.MenuItem("❌ Thoát", exit_app),
    ])
    
    menu = pystray.Menu(*menu_items)
    
    # Create icon
    icon = pystray.Icon(
        APP_NAME,
        create_icon_image(),
        f"{APP_NAME} v{APP_VERSION}",
        menu
    )
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Small delay before showing notification
    import time
    time.sleep(2)
    
    # Show notification
    try:
        icon.notify(
            f"Đang chạy ngầm\nMở Dashboard: {DASHBOARD_URL}",
            APP_NAME
        )
    except:
        pass  # Notification might fail on some systems
    
    # Run tray icon (blocking)
    print("🔔 System tray icon active. Right-click to see options.")
    icon.run()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description=f"{APP_NAME} v{APP_VERSION}")
    parser.add_argument("--hidden", "-H", action="store_true", 
                        help="Run in background mode with system tray")
    parser.add_argument("--no-tray", action="store_true",
                        help="Run without system tray (foreground mode)")
    parser.add_argument("--startup-enable", action="store_true",
                        help="Enable startup with Windows")
    parser.add_argument("--startup-disable", action="store_true",
                        help="Disable startup with Windows")
    
    args = parser.parse_args()
    
    # Handle startup options
    if args.startup_enable:
        if STARTUP_AVAILABLE:
            enable_startup(sys.executable, run_hidden=True)
        else:
            print("❌ Startup manager không khả dụng")
        return
    
    if args.startup_disable:
        if STARTUP_AVAILABLE:
            disable_startup()
        else:
            print("❌ Startup manager không khả dụng")
        return
    
    # Run mode
    if args.hidden and not args.no_tray:
        # Background mode with system tray
        run_with_tray()
    else:
        # Foreground mode
        run_server()

if __name__ == "__main__":
    main()
