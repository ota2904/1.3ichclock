"""
miniZ MCP Installer Setup Script
Tạo file cài đặt EXE với license key validation
"""

import os
import sys
import json
import hashlib
import platform
from pathlib import Path
from datetime import datetime, timedelta

# ============================================================
# LICENSE KEY GENERATION & VALIDATION
# ============================================================

def generate_hardware_id():
    """Tạo hardware ID dựa trên thông tin máy"""
    try:
        import uuid
        import subprocess
        
        # Get MAC address
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0,2*6,2)][::-1])
        
        # Get CPU info
        try:
            if platform.system() == "Windows":
                cpu_info = subprocess.check_output("wmic cpu get processorid", shell=True).decode()
                cpu_id = cpu_info.split('\n')[1].strip() if len(cpu_info.split('\n')) > 1 else ""
            else:
                cpu_id = ""
        except:
            cpu_id = ""
        
        # Combine and hash
        combined = f"{mac}{cpu_id}{platform.node()}"
        hardware_id = hashlib.sha256(combined.encode()).hexdigest()[:32].upper()
        
        return hardware_id
    except Exception as e:
        print(f"Error generating hardware ID: {e}")
        return None

def generate_license_key(hardware_id, customer_name="User", license_type="standard", days=365):
    """
    Tạo license key cho hardware ID cụ thể
    Format: XXXX-XXXX-XXXX-XXXX-XXXX
    """
    import secrets
    
    # Create payload
    expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y%m%d")
    
    payload = {
        "hwid": hardware_id,
        "customer": customer_name,
        "type": license_type,  # standard, pro, enterprise
        "expiry": expiry_date,
        "version": "4.3.0"
    }
    
    # Generate signature
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hashlib.sha256(payload_str.encode()).hexdigest()[:20]
    
    # Combine into license key
    combined = f"{hardware_id[:8]}{signature}"
    
    # Format as XXXX-XXXX-XXXX-XXXX-XXXX
    key_parts = [combined[i:i+4] for i in range(0, 20, 4)]
    license_key = "-".join(key_parts).upper()
    
    return license_key, payload

def validate_license_key(license_key, hardware_id):
    """Kiểm tra license key có hợp lệ không"""
    try:
        # Remove dashes
        clean_key = license_key.replace("-", "")
        
        if len(clean_key) != 20:
            return False, "Invalid key format"
        
        # Extract hardware ID from key
        key_hwid = clean_key[:8]
        
        # Check if hardware ID matches
        if key_hwid != hardware_id[:8]:
            return False, "License key không khớp với máy tính này"
        
        return True, "Valid license"
        
    except Exception as e:
        return False, str(e)

# ============================================================
# INSTALLER GUI
# ============================================================

def create_installer_gui():
    """Tạo GUI cho installer với tkinter"""
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, filedialog
    except ImportError:
        print("Error: tkinter not found. Please install it.")
        return
    
    class InstallerGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("miniZ MCP v4.3.0 - Installer")
            self.root.geometry("600x700")
            self.root.resizable(False, False)
            
            # Variables
            self.license_key_var = tk.StringVar()
            self.install_path_var = tk.StringVar(value=str(Path.home() / "miniZ_MCP"))
            self.agree_var = tk.BooleanVar()
            
            # Get hardware ID
            self.hardware_id = generate_hardware_id()
            
            self.setup_ui()
        
        def setup_ui(self):
            # Header
            header_frame = tk.Frame(self.root, bg="#667eea", height=100)
            header_frame.pack(fill=tk.X)
            
            title = tk.Label(header_frame, text="🚀 miniZ MCP", 
                           font=("Arial", 24, "bold"), bg="#667eea", fg="white")
            title.pack(pady=10)
            
            subtitle = tk.Label(header_frame, text="Professional Edition v4.3.0", 
                              font=("Arial", 12), bg="#667eea", fg="white")
            subtitle.pack()
            
            # Main content
            main_frame = tk.Frame(self.root, padx=30, pady=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Welcome message
            welcome = tk.Label(main_frame, 
                             text="Chào mừng đến với miniZ MCP Installer!\n"
                                  "Điều khiển máy tính thông minh với AI và Voice Control",
                             font=("Arial", 10), justify=tk.LEFT, wraplength=500)
            welcome.pack(pady=(0, 20))
            
            # Hardware ID section
            hw_frame = tk.LabelFrame(main_frame, text="🔑 Hardware ID", 
                                    font=("Arial", 10, "bold"), padx=10, pady=10)
            hw_frame.pack(fill=tk.X, pady=(0, 15))
            
            hw_label = tk.Label(hw_frame, text=f"Hardware ID: {self.hardware_id}", 
                              font=("Courier", 9), fg="#667eea")
            hw_label.pack()
            
            hw_note = tk.Label(hw_frame, 
                             text="Gửi Hardware ID này cho nhà cung cấp để nhận license key",
                             font=("Arial", 8), fg="gray")
            hw_note.pack()
            
            copy_btn = tk.Button(hw_frame, text="📋 Copy Hardware ID", 
                               command=self.copy_hardware_id)
            copy_btn.pack(pady=5)
            
            # License Key section
            license_frame = tk.LabelFrame(main_frame, text="🔐 License Key", 
                                        font=("Arial", 10, "bold"), padx=10, pady=10)
            license_frame.pack(fill=tk.X, pady=(0, 15))
            
            license_entry = tk.Entry(license_frame, textvariable=self.license_key_var,
                                   font=("Arial", 12), width=35)
            license_entry.pack(pady=5)
            
            license_hint = tk.Label(license_frame, 
                                  text="Format: XXXX-XXXX-XXXX-XXXX-XXXX",
                                  font=("Arial", 8), fg="gray")
            license_hint.pack()
            
            validate_btn = tk.Button(license_frame, text="✅ Kiểm tra License", 
                                   command=self.validate_license, bg="#10b981", fg="white")
            validate_btn.pack(pady=5)
            
            # Install path section
            path_frame = tk.LabelFrame(main_frame, text="📁 Thư mục cài đặt", 
                                     font=("Arial", 10, "bold"), padx=10, pady=10)
            path_frame.pack(fill=tk.X, pady=(0, 15))
            
            path_entry_frame = tk.Frame(path_frame)
            path_entry_frame.pack(fill=tk.X)
            
            path_entry = tk.Entry(path_entry_frame, textvariable=self.install_path_var,
                                font=("Arial", 10), width=40)
            path_entry.pack(side=tk.LEFT, padx=(0, 5))
            
            browse_btn = tk.Button(path_entry_frame, text="📂 Browse", 
                                  command=self.browse_path)
            browse_btn.pack(side=tk.LEFT)
            
            # Agreement checkbox
            agree_frame = tk.Frame(main_frame)
            agree_frame.pack(fill=tk.X, pady=(0, 15))
            
            agree_check = tk.Checkbutton(agree_frame, variable=self.agree_var,
                                        text="Tôi đồng ý với điều khoản sử dụng và chính sách bảo mật",
                                        font=("Arial", 9))
            agree_check.pack()
            
            terms_link = tk.Label(agree_frame, text="Xem điều khoản", 
                                font=("Arial", 8), fg="blue", cursor="hand2")
            terms_link.pack()
            terms_link.bind("<Button-1>", lambda e: self.show_terms())
            
            # Install button
            install_btn = tk.Button(main_frame, text="🚀 Cài đặt miniZ MCP", 
                                  command=self.install, bg="#667eea", fg="white",
                                  font=("Arial", 12, "bold"), height=2)
            install_btn.pack(fill=tk.X, pady=10)
            
            # Footer
            footer = tk.Label(main_frame, 
                            text="© 2024-2025 miniZ MCP. All rights reserved.",
                            font=("Arial", 8), fg="gray")
            footer.pack(side=tk.BOTTOM)
        
        def copy_hardware_id(self):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.hardware_id)
            messagebox.showinfo("Success", "Hardware ID đã được copy vào clipboard!")
        
        def validate_license(self):
            license_key = self.license_key_var.get().strip()
            
            if not license_key:
                messagebox.showerror("Error", "Vui lòng nhập license key!")
                return
            
            is_valid, message = validate_license_key(license_key, self.hardware_id)
            
            if is_valid:
                messagebox.showinfo("✅ Success", 
                                  "License key hợp lệ!\nBạn có thể tiến hành cài đặt.")
            else:
                messagebox.showerror("❌ Invalid License", message)
        
        def browse_path(self):
            path = filedialog.askdirectory(title="Chọn thư mục cài đặt")
            if path:
                self.install_path_var.set(path)
        
        def show_terms(self):
            terms = """
ĐIỀU KHOẢN SỬ DỤNG MINIZ MCP v4.3.0

1. GIẤY PHÉP
Software này được cấp phép cho một máy tính duy nhất.
License key chỉ hoạt động trên máy tính có Hardware ID tương ứng.

2. BẢO MẬT
- Không chia sẻ license key cho người khác
- Không decompile hoặc reverse engineer
- Không sử dụng cho mục đích thương mại trừ khi có license Enterprise

3. HỖ TRỢ & CẬP NHẬT
- Hỗ trợ kỹ thuật qua email
- Cập nhật miễn phí trong 1 năm
- Gia hạn license sau khi hết hạn

4. GIỚI HẠN TRÁCH NHIỆM
Software được cung cấp "AS IS" không có bảo hành.
Nhà phát triển không chịu trách nhiệm về thiệt hại phát sinh.

5. BẢN QUYỀN
© 2024-2025 miniZ MCP. All rights reserved.
"""
            top = tk.Toplevel(self.root)
            top.title("Điều khoản sử dụng")
            top.geometry("500x400")
            
            text = tk.Text(top, wrap=tk.WORD, padx=10, pady=10)
            text.pack(fill=tk.BOTH, expand=True)
            text.insert("1.0", terms)
            text.config(state=tk.DISABLED)
            
            close_btn = tk.Button(top, text="Đóng", command=top.destroy)
            close_btn.pack(pady=10)
        
        def install(self):
            # Validate inputs
            license_key = self.license_key_var.get().strip()
            install_path = Path(self.install_path_var.get())
            
            if not license_key:
                messagebox.showerror("Error", "Vui lòng nhập license key!")
                return
            
            if not self.agree_var.get():
                messagebox.showerror("Error", "Vui lòng đồng ý với điều khoản sử dụng!")
                return
            
            # Validate license
            is_valid, message = validate_license_key(license_key, self.hardware_id)
            if not is_valid:
                messagebox.showerror("Invalid License", message)
                return
            
            # Start installation
            if messagebox.askyesno("Xác nhận", 
                                  f"Cài đặt miniZ MCP vào:\n{install_path}\n\nTiếp tục?"):
                try:
                    self.perform_installation(install_path, license_key)
                except Exception as e:
                    messagebox.showerror("Installation Error", str(e))
        
        def perform_installation(self, install_path, license_key):
            """Thực hiện cài đặt"""
            import shutil
            import time
            
            # Create progress window
            progress_win = tk.Toplevel(self.root)
            progress_win.title("Installing...")
            progress_win.geometry("400x150")
            progress_win.transient(self.root)
            progress_win.grab_set()
            
            tk.Label(progress_win, text="Đang cài đặt miniZ MCP...", 
                    font=("Arial", 12)).pack(pady=20)
            
            progress_bar = ttk.Progressbar(progress_win, length=300, mode='determinate')
            progress_bar.pack(pady=10)
            
            status_label = tk.Label(progress_win, text="", font=("Arial", 9))
            status_label.pack()
            
            # Installation steps
            steps = [
                ("Tạo thư mục cài đặt...", 20),
                ("Copy files...", 40),
                ("Cài đặt dependencies...", 60),
                ("Tạo license file...", 80),
                ("Hoàn tất cài đặt...", 100)
            ]
            
            for step_name, progress in steps:
                status_label.config(text=step_name)
                progress_bar['value'] = progress
                progress_win.update()
                time.sleep(0.5)
                
                # Perform actual step
                if "thư mục" in step_name:
                    install_path.mkdir(parents=True, exist_ok=True)
                
                elif "Copy" in step_name:
                    # Copy application files
                    source_dir = Path(__file__).parent
                    files_to_copy = ['xiaozhi_final.py', 'requirements.txt', 
                                    'START.bat', 'README.md']
                    
                    for file in files_to_copy:
                        src = source_dir / file
                        if src.exists():
                            shutil.copy2(src, install_path / file)
                    
                    # Copy music_library
                    if (source_dir / 'music_library').exists():
                        shutil.copytree(source_dir / 'music_library', 
                                      install_path / 'music_library', 
                                      dirs_exist_ok=True)
                
                elif "license" in step_name:
                    # Create license file
                    license_data = {
                        "license_key": license_key,
                        "hardware_id": self.hardware_id,
                        "install_date": datetime.now().isoformat(),
                        "version": "4.3.0"
                    }
                    
                    with open(install_path / ".license", 'w') as f:
                        json.dump(license_data, f, indent=2)
            
            progress_win.destroy()
            
            # Installation complete
            messagebox.showinfo("✅ Success", 
                              f"Cài đặt thành công!\n\n"
                              f"Thư mục: {install_path}\n\n"
                              f"Chạy START.bat để khởi động miniZ MCP")
            
            self.root.destroy()
    
    # Run GUI
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()

# ============================================================
# COMMAND LINE TOOLS
# ============================================================

def generate_license_cli():
    """CLI tool để generate license key"""
    print("\n" + "="*60)
    print("    miniZ MCP - License Key Generator")
    print("="*60 + "\n")
    
    hardware_id = input("Enter Hardware ID: ").strip()
    customer_name = input("Customer Name [User]: ").strip() or "User"
    license_type = input("License Type (standard/pro/enterprise) [standard]: ").strip() or "standard"
    days = input("Valid Days [365]: ").strip()
    days = int(days) if days.isdigit() else 365
    
    license_key, payload = generate_license_key(hardware_id, customer_name, license_type, days)
    
    print("\n" + "="*60)
    print("✅ License Key Generated Successfully!")
    print("="*60)
    print(f"\nLicense Key: {license_key}")
    print(f"\nCustomer: {customer_name}")
    print(f"Type: {license_type}")
    print(f"Expiry: {payload['expiry']}")
    print(f"Hardware ID: {hardware_id}")
    print("\n" + "="*60 + "\n")
    
    # Save to file
    with open("license_info.txt", "w") as f:
        f.write(f"miniZ MCP v4.3.0 - License Information\n")
        f.write("="*60 + "\n\n")
        f.write(f"License Key: {license_key}\n")
        f.write(f"Customer: {customer_name}\n")
        f.write(f"Type: {license_type}\n")
        f.write(f"Expiry: {payload['expiry']}\n")
        f.write(f"Hardware ID: {hardware_id}\n")
    
    print("📄 License info saved to: license_info.txt")

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "generate":
            generate_license_cli()
        elif sys.argv[1] == "hwid":
            hwid = generate_hardware_id()
            print(f"\n🔑 Hardware ID: {hwid}\n")
    else:
        # Run installer GUI
        create_installer_gui()
