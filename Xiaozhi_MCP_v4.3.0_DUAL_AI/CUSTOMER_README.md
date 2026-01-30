# miniZ MCP Professional v4.3.0 - Customer Edition

## 🎯 Giới Thiệu

**miniZ MCP Professional** là trợ lý AI đa năng với hệ thống license hardware-locked bảo mật cao, hỗ trợ:
- ✅ Dual AI (GPT-4 + Gemini)
- ✅ Music Library Management
- ✅ Multi-language Support
- ✅ Lifetime License (không giới hạn thời gian)

---

## 📦 Package Contents

```
miniZ_MCP_Professional/
├── miniZ_MCP_Professional.exe (132 MB)
├── LICENSE_ACTIVATION_GUIDE.md (Full documentation)
├── CUSTOMER_README.md (This file)
└── Sample_Keys.txt (Test keys)
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Run Application
Double-click: `miniZ_MCP_Professional.exe`

### Step 2: Enter License Key
When prompted, enter your license key:
```
Format: MINIZ-XXXX-XXXX-XXXX-XXXX
Example: MINIZ-STD5-G3YE-7L5J-57ND
```

### Step 3: Start Using
License activated! App will remember your activation.

---

## 🔐 License Tiers

| Tier | Devices | Features |
|------|---------|----------|
| **STANDARD** | 1 device | Full AI features, Music library |
| **PRO** | 2 devices | Standard + Priority support |
| **ENTERPRISE** | 5 devices | Pro + Team management |

**All tiers include:**
- ✅ Lifetime validity (no expiration)
- ✅ Free updates
- ✅ Hardware-locked security

---

## 🔧 System Requirements

- **OS**: Windows 10/11 (64-bit)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Storage**: 500 MB free space
- **Internet**: Required for AI features

---

## 📋 Sample License Keys (For Testing)

### STANDARD Keys
```
MINIZ-STD5-G3YE-7L5J-57ND
MINIZ-STDD-NF2L-4Z3N-PXCV
MINIZ-STD4-QKJT-8JF5-HVVJ
```

### PRO Keys
```
MINIZ-PRO6-D8SM-J3NK-G7R4
MINIZ-PROB-ZDFC-LDS7-UB32
```

### ENTERPRISE Keys
```
MINIZ-ENTJ-VFTV-K6VQ-8UZD
MINIZ-ENTU-6KYR-UYX8-CN99
```

> ⚠️ **NOTE**: These are sample keys. Your purchased key will be unique.

---

## 🔐 Security Architecture

### Hardware Binding
License is bound to your computer's:
- ✅ CPU Processor ID
- ✅ Motherboard Serial Number

**Result**: License cannot be copied to another computer.

### Encryption
- **Algorithm**: AES-256 Fernet
- **Key Derivation**: PBKDF2HMAC-SHA256
- **Iterations**: 100,000
- **Storage**: `%LOCALAPPDATA%\miniZ_MCP\.license\license.enc`

### License File Location
```
C:\Users\<YourUsername>\AppData\Local\miniZ_MCP\.license\license.enc
```

> ⚠️ **IMPORTANT**: Do NOT delete this file. It contains your encrypted license.

---

## ❓ Troubleshooting

### Problem: "License key format không hợp lệ"
**Solution**: 
- Check key format: Must be `MINIZ-XXXX-XXXX-XXXX-XXXX`
- Ensure no spaces or extra characters
- Copy-paste carefully from email/document

### Problem: "License key không tồn tại"
**Solution**:
- Verify key is from official source
- Contact support if key was purchased
- Try sample keys for testing

### Problem: "License không khớp với máy này"
**Reason**: License file was copied from another computer.
**Solution**:
- Delete: `%LOCALAPPDATA%\miniZ_MCP\.license\license.enc`
- Re-activate with your license key
- Each device needs separate activation

### Problem: App won't start
**Solution**:
- Right-click EXE → "Run as Administrator"
- Check Windows Defender/Antivirus exclusions
- Ensure .NET Framework installed

---

## 📞 Support

### Get Your Hardware ID
For support or multi-device activation:
```python
# Run this in Python to get your Hardware ID
import hashlib, subprocess

def get_hardware_id():
    cpu_result = subprocess.check_output("wmic cpu get ProcessorId", shell=True, text=True)
    cpu_id = cpu_result.strip().split('\n')[1].strip()
    
    mobo_result = subprocess.check_output("wmic baseboard get SerialNumber", shell=True, text=True)
    mobo_serial = mobo_result.strip().split('\n')[1].strip()
    
    raw_id = f"{cpu_id}:{mobo_serial}"
    hardware_id = hashlib.sha256(raw_id.encode()).hexdigest()[:32].upper()
    return hardware_id

print(f"Your Hardware ID: {get_hardware_id()}")
```

### Contact Information
- **Email**: support@example.com (Update with your support email)
- **Website**: https://example.com (Update with your website)
- **Documentation**: See `LICENSE_ACTIVATION_GUIDE.md` for complete details

---

## 🔄 Update Policy

- **Lifetime License**: No recurring fees
- **Free Updates**: Minor version updates included (v4.x.x)
- **Major Versions**: May require upgrade license (v5.0.0+)

---

## 📜 License Agreement

By using this software, you agree to:
1. Use license only on authorized number of devices (per tier)
2. Not share license keys with others
3. Not attempt to crack, reverse engineer, or bypass license system
4. Not redistribute the software without authorization

**License Validity**: Lifetime (no expiration)
**Support Period**: 1 year from purchase (can be extended)

---

## 🎓 User Guide Quick Reference

### Activate License (First Time)
1. Run `miniZ_MCP_Professional.exe`
2. Enter license key when prompted
3. See "✅ License XXXX đã được kích hoạt thành công!"

### Check License Status
```python
# In Python console within app
from license_manager import get_license_manager
manager = get_license_manager()
status = manager.validate_license()
print(status)
```

### View Hardware ID
```python
# In Python console within app
from license_system import get_hardware_id
print(f"Hardware ID: {get_hardware_id()}")
```

---

## 📊 Build Information

- **Version**: 4.3.0
- **Build Date**: 2025-01-08
- **Python**: 3.13.9
- **Architecture**: Windows x64
- **File Size**: 132 MB
- **License System**: Hardware-locked AES-256

---

## 🌟 Features Overview

### AI Capabilities
- GPT-4 and Gemini integration
- Multi-language conversation
- Context-aware responses
- API endpoint management

### Music Library
- Organize by genre (Classical, Pop, Rock)
- Metadata management
- Playlist creation
- Search and filter

### Additional Features
- Windows startup integration
- Auto-update checker
- Multi-user support (Enterprise)
- Command-line interface

---

## ⚖️ Legal

**Copyright © 2025 miniZ MCP**
All rights reserved.

This software is licensed, not sold. Unauthorized distribution, copying, or modification is prohibited and may result in license revocation.

For full terms and conditions, see LICENSE file.

---

**Thank you for choosing miniZ MCP Professional!**

For complete documentation, see: `LICENSE_ACTIVATION_GUIDE.md`
