# miniZ MCP - Icon Setup Guide

## 🎨 ICON REQUIREMENTS

Để installer có icon đẹp, cần tạo các file sau:

### 1. icon.ico (Application Icon)
- **Format:** .ico
- **Size:** 256x256, 128x128, 64x64, 48x48, 32x32, 16x16
- **Usage:** Desktop shortcut, taskbar, file icon

### 2. installer_banner.bmp (Installer Banner)
- **Format:** .bmp
- **Size:** 164 x 314 pixels
- **Usage:** Left side of installer wizard
- **Design:** Logo + branding

### 3. installer_icon.bmp (Installer Small Icon)
- **Format:** .bmp  
- **Size:** 55 x 58 pixels
- **Usage:** Top-right corner of installer
- **Design:** Small logo/icon

---

## 🛠️ TẠO ICON

### Cách 1: Sử dụng Online Tools

**Icon Converter:**
```
1. Tạo logo 512x512 PNG
2. Upload lên: https://convertico.com/
3. Convert to .ico
4. Download và rename thành icon.ico
```

**BMP Creator:**
```
1. Tạo ảnh đúng kích thước
2. Save as .bmp (24-bit)
3. Đặt tên theo yêu cầu
```

### Cách 2: Sử dụng GIMP/Photoshop

```
1. Mở GIMP/Photoshop
2. Tạo ảnh 512x512
3. Design logo miniZ MCP
4. Export:
   - icon.ico (multi-size)
   - installer_banner.bmp (164x314)
   - installer_icon.bmp (55x58)
```

### Cách 3: Thuê Designer

```
Yêu cầu designer tạo:
- Logo vector
- Icon set (.ico multi-resolution)
- Installer banners (.bmp)
```

---

## 📐 DESIGN GUIDELINES

### Logo Design
```
✓ Simple, professional
✓ Readable at small sizes
✓ Colors: #667eea (primary), white/gray
✓ Theme: AI, Technology, Control
```

### Banner Design
```
✓ Vertical layout (164x314)
✓ Logo at top
✓ Text: "miniZ MCP v4.3.0"
✓ Background: Gradient or solid color
✓ Professional appearance
```

### Small Icon
```
✓ Square (55x58)
✓ Clear at small size
✓ Simple shape
✓ High contrast
```

---

## 🚀 TEMPORARY SOLUTION

Nếu chưa có icon, installer vẫn hoạt động:

```iss
; Trong setup_inno.iss, comment out icon lines:
; SetupIconFile=icon.ico
; WizardImageFile=installer_banner.bmp
; WizardSmallImageFile=installer_icon.bmp
; UninstallDisplayIcon={app}\icon.ico
```

Installer sẽ dùng icon mặc định của Windows.

---

## ✅ CHECK

Sau khi tạo xong:

```
✓ icon.ico - 256x256 hoặc lớn hơn
✓ installer_banner.bmp - 164x314 pixels
✓ installer_icon.bmp - 55x58 pixels
✓ All files in project root
✓ Rebuild installer
```

---

## 🎨 SAMPLE DESIGN IDEAS

### Logo Concepts
```
Idea 1: Chip + Voice Wave
  💻 🎤 → Modern, tech-focused

Idea 2: "MZ" Monogram
  🅼🆉 → Simple, memorable

Idea 3: AI Brain Circuit
  🧠⚡ → AI-themed
```

### Color Schemes
```
Scheme 1: Purple/Blue
  Primary: #667eea
  Secondary: #764ba2
  
Scheme 2: Blue/Cyan
  Primary: #3b82f6
  Secondary: #06b6d4

Scheme 3: Dark/Accent
  Primary: #1e293b
  Accent: #10b981
```

---

## 📝 QUICK FIX

Nếu cần icon ngay:

```python
# Tạo icon đơn giản bằng Python + Pillow
from PIL import Image, ImageDraw, ImageFont

# Create 256x256 icon
img = Image.new('RGBA', (256, 256), (102, 126, 234, 255))
draw = ImageDraw.Draw(img)

# Draw simple "MZ" text
font = ImageFont.truetype("arial.ttf", 120)
draw.text((50, 50), "MZ", fill=(255, 255, 255, 255), font=font)

# Save as PNG then convert to .ico
img.save('icon.png')
# Convert online: https://convertico.com/
```

---

Without icons, installer will work but look less professional.
With icons, it looks complete and polished! 🎨✨
