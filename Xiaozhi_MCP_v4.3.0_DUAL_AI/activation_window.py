"""
miniZ MCP v4.3.0 - License Activation Window
Beautiful GUI for license activation
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from license_manager import get_license_manager


class ActivationWindow:
    """Professional license activation window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("miniZ MCP v4.3.0 - Kích Hoạt License")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (650 // 2)
        self.root.geometry(f"600x650+{x}+{y}")
        
        # Colors
        self.bg_color = "#1a1a2e"
        self.accent_color = "#667eea"
        self.text_color = "#ffffff"
        self.input_bg = "#16213e"
        
        self.license_manager = get_license_manager()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=self.accent_color, height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🚀 miniZ MCP v4.3.0",
            font=("Segoe UI", 24, "bold"),
            bg=self.accent_color,
            fg=self.text_color
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Phần mềm điều khiển máy tính chuyên nghiệp",
            font=("Segoe UI", 11),
            bg=self.accent_color,
            fg=self.text_color
        )
        subtitle_label.pack()
        
        # Content frame
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40)
        
        # Hardware ID section
        hw_frame = tk.Frame(content_frame, bg=self.bg_color)
        hw_frame.pack(fill=tk.X, pady=(0, 20))
        
        hw_label = tk.Label(
            hw_frame,
            text="🔑 Hardware ID (Machine ID):",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        hw_label.pack(anchor=tk.W, pady=(0, 5))
        
        hw_id_frame = tk.Frame(hw_frame, bg=self.input_bg, relief=tk.FLAT)
        hw_id_frame.pack(fill=tk.X)
        
        self.hw_id_text = tk.Text(
            hw_id_frame,
            height=2,
            font=("Consolas", 10),
            bg=self.input_bg,
            fg="#00ff00",
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10
        )
        self.hw_id_text.pack(fill=tk.X)
        self.hw_id_text.insert("1.0", self.license_manager.get_hardware_id())
        self.hw_id_text.config(state=tk.DISABLED)
        
        copy_hw_btn = tk.Button(
            hw_frame,
            text="📋 Copy Hardware ID",
            font=("Segoe UI", 9),
            bg=self.input_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            cursor="hand2",
            command=self.copy_hardware_id
        )
        copy_hw_btn.pack(anchor=tk.E, pady=(5, 0))
        
        # License key section
        key_label = tk.Label(
            content_frame,
            text="🎫 Nhập License Key:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        key_label.pack(anchor=tk.W, pady=(10, 5))
        
        key_entry_frame = tk.Frame(content_frame, bg=self.input_bg, relief=tk.FLAT)
        key_entry_frame.pack(fill=tk.X)
        
        self.key_entry = tk.Entry(
            key_entry_frame,
            font=("Consolas", 14, "bold"),
            bg=self.input_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            insertbackground=self.text_color,
            justify=tk.CENTER
        )
        self.key_entry.pack(fill=tk.X, padx=10, pady=10)
        self.key_entry.insert(0, "XXXX-XXXX-XXXX-XXXX")
        self.key_entry.bind("<FocusIn>", lambda e: self.key_entry.delete(0, tk.END) if self.key_entry.get() == "XXXX-XXXX-XXXX-XXXX" else None)
        
        # Format hint
        hint_label = tk.Label(
            content_frame,
            text="Định dạng: XXXX-XXXX-XXXX-XXXX (16 ký tự, không phân biệt hoa thường)",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg="#888888"
        )
        hint_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Offline mode checkbox
        self.offline_var = tk.BooleanVar(value=False)
        offline_check = tk.Checkbutton(
            content_frame,
            text="Chế độ Offline (không kết nối server)",
            variable=self.offline_var,
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_color,
            selectcolor=self.input_bg,
            activebackground=self.bg_color,
            activeforeground=self.text_color
        )
        offline_check.pack(anchor=tk.W, pady=(10, 0))
        
        # Buttons frame
        btn_frame = tk.Frame(content_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=(30, 0))
        
        self.activate_btn = tk.Button(
            btn_frame,
            text="✅ Kích Hoạt",
            font=("Segoe UI", 12, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            relief=tk.FLAT,
            cursor="hand2",
            width=15,
            command=self.activate_license
        )
        self.activate_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_btn = tk.Button(
            btn_frame,
            text="❌ Thoát",
            font=("Segoe UI", 12, "bold"),
            bg=self.input_bg,
            fg=self.text_color,
            relief=tk.FLAT,
            cursor="hand2",
            width=15,
            command=self.root.quit
        )
        exit_btn.pack(side=tk.LEFT)
        
        # Status label
        self.status_label = tk.Label(
            content_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg="#ffcc00",
            wraplength=500,
            justify=tk.LEFT
        )
        self.status_label.pack(anchor=tk.W, pady=(15, 0))
        
        # Footer
        footer_label = tk.Label(
            main_frame,
            text="© 2025 miniZ Team | Hỗ trợ: support@miniz-mcp.com",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg="#666666"
        )
        footer_label.pack(side=tk.BOTTOM, pady=10)
        
    def copy_hardware_id(self):
        """Copy hardware ID to clipboard"""
        hw_id = self.license_manager.get_hardware_id()
        self.root.clipboard_clear()
        self.root.clipboard_append(hw_id)
        self.status_label.config(
            text="✅ Đã copy Hardware ID vào clipboard!",
            fg="#00ff00"
        )
        
    def activate_license(self):
        """Activate the license key"""
        license_key = self.key_entry.get().strip()
        
        if not license_key or license_key == "XXXX-XXXX-XXXX-XXXX":
            messagebox.showwarning(
                "Thiếu thông tin",
                "Vui lòng nhập License Key!"
            )
            return
        
        # Disable button during activation
        self.activate_btn.config(state=tk.DISABLED, text="⏳ Đang kích hoạt...")
        self.status_label.config(
            text="🔄 Đang xác thực license key...",
            fg="#ffcc00"
        )
        self.root.update()
        
        # Run activation in thread to prevent UI freeze
        def activate_thread():
            # Always use offline mode for instant activation (no server check)
            offline_mode = True  # Force offline for instant activation
            result = self.license_manager.activate_license(license_key, offline_mode)
            
            # Update UI from main thread
            self.root.after(0, lambda: self.show_activation_result(result))
        
        threading.Thread(target=activate_thread, daemon=True).start()
    
    def show_activation_result(self, result):
        """Show activation result"""
        self.activate_btn.config(state=tk.NORMAL, text="✅ Kích Hoạt")
        
        if result['success']:
            self.status_label.config(
                text=result['message'],
                fg="#00ff00"
            )
            messagebox.showinfo(
                "Thành công",
                result['message'] + "\n\nPhần mềm sẽ khởi động sau khi bạn nhấn OK."
            )
            self.root.quit()
        else:
            self.status_label.config(
                text=result['message'],
                fg="#ff4444"
            )
            messagebox.showerror(
                "Lỗi",
                result['message']
            )
    
    def run(self):
        """Run the activation window"""
        self.root.mainloop()
        return self.license_manager.check_license()['valid']


def show_activation_window() -> bool:
    """Show activation window and return True if activated"""
    window = ActivationWindow()
    return window.run()


if __name__ == "__main__":
    activated = show_activation_window()
    if activated:
        print("✅ License activated successfully!")
    else:
        print("❌ License activation failed or cancelled")
