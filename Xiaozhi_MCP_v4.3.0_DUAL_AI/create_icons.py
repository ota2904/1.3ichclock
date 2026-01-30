"""
🎨 miniZ MCP - Icon Generator
Tạo icon .ico từ gradient design
"""

import os
import sys
from pathlib import Path

def create_icon():
    """Create icon using PIL"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Installing Pillow...")
        os.system(f"{sys.executable} -m pip install Pillow --quiet")
        from PIL import Image, ImageDraw, ImageFont
    
    # Icon sizes for .ico file
    sizes = [256, 128, 64, 48, 32, 16]
    images = []
    
    for size in sizes:
        # Create image with transparency
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient circle
        cx, cy = size // 2, size // 2
        radius = size // 2 - 2
        
        for y in range(size):
            for x in range(size):
                # Check if inside circle
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                
                if dist <= radius:
                    # Gradient from #667eea (top) to #764ba2 (bottom)
                    ratio = y / size
                    r = int(102 + (118 - 102) * ratio)
                    g = int(126 + (75 - 126) * ratio)
                    b = int(234 + (162 - 234) * ratio)
                    
                    # Anti-aliasing at edges
                    if dist > radius - 1.5:
                        alpha = int(255 * max(0, (radius - dist + 1.5) / 1.5))
                    else:
                        alpha = 255
                    
                    img.putpixel((x, y), (r, g, b, alpha))
        
        # Draw "MZ" text if size is large enough
        if size >= 32:
            try:
                # Try to use Arial font
                font_size = size // 3
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                
                text = "MZ"
                
                # Get text bounding box
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except AttributeError:
                    text_width, text_height = font_size * 2, font_size
                
                text_x = (size - text_width) // 2
                text_y = (size - text_height) // 2 - size // 10
                
                # Draw text with shadow
                shadow_offset = max(1, size // 32)
                draw.text((text_x + shadow_offset, text_y + shadow_offset), text, 
                         fill=(0, 0, 0, 100), font=font)
                draw.text((text_x, text_y), text, fill='white', font=font)
                
            except Exception as e:
                print(f"Warning: Could not draw text: {e}")
        
        images.append(img)
    
    # Save as .ico
    base_dir = Path(__file__).parent
    ico_path = base_dir / "miniz_icon.ico"
    
    # Save the largest image first, then include all sizes
    images[0].save(
        str(ico_path),
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    
    print(f"✅ Created: {ico_path}")
    
    # Also save as PNG for other uses
    png_path = base_dir / "miniz_icon.png"
    images[0].save(str(png_path), format='PNG')
    print(f"✅ Created: {png_path}")
    
    return ico_path

def create_installer_banner():
    """Create banner for Inno Setup installer"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    
    # Inno Setup wizard image: 164x314
    width, height = 164, 314
    img = Image.new('RGB', (width, height), '#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for y in range(height):
        ratio = y / height
        r = int(26 + (102 - 26) * ratio * 0.5)
        g = int(26 + (126 - 26) * ratio * 0.5)
        b = int(46 + (234 - 46) * ratio * 0.5)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Draw logo circle at top
    cx, cy = width // 2, 80
    radius = 50
    
    for y in range(cy - radius, cy + radius):
        for x in range(cx - radius, cx + radius):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= radius:
                ratio = (y - (cy - radius)) / (radius * 2)
                r = int(102 + (118 - 102) * ratio)
                g = int(126 + (75 - 126) * ratio)
                b = int(234 + (162 - 234) * ratio)
                if 0 <= x < width and 0 <= y < height:
                    img.putpixel((x, y), (r, g, b))
    
    # Draw "MZ" in circle
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    
    draw.text((cx, cy), "MZ", fill='white', font=font, anchor='mm')
    
    # Draw "miniZ MCP" text
    try:
        title_font = ImageFont.truetype("arial.ttf", 18)
        version_font = ImageFont.truetype("arial.ttf", 12)
    except:
        title_font = version_font = ImageFont.load_default()
    
    draw.text((cx, 160), "miniZ", fill='#667eea', font=title_font, anchor='mm')
    draw.text((cx, 180), "MCP", fill='#764ba2', font=title_font, anchor='mm')
    draw.text((cx, 210), "v4.3.0", fill='#888888', font=version_font, anchor='mm')
    
    # Draw feature list
    features = [
        "🤖 AI Control",
        "🎵 Music Player",
        "🔍 Web Search",
        "💬 Chat History"
    ]
    
    try:
        small_font = ImageFont.truetype("arial.ttf", 10)
    except:
        small_font = ImageFont.load_default()
    
    y_start = 250
    for i, feature in enumerate(features):
        draw.text((cx, y_start + i * 15), feature, fill='#cccccc', 
                 font=small_font, anchor='mm')
    
    # Save
    base_dir = Path(__file__).parent
    banner_path = base_dir / "installer_banner.bmp"
    img.save(str(banner_path), format='BMP')
    print(f"✅ Created: {banner_path}")
    
    return banner_path

def create_installer_header():
    """Create header image for Inno Setup (150x57)"""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None
    
    # Inno Setup header: 150x57
    width, height = 150, 57
    img = Image.new('RGB', (width, height), '#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Draw gradient
    for x in range(width):
        ratio = x / width
        r = int(102 + (118 - 102) * ratio)
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        draw.line([(x, 0), (x, height)], fill=(r, g, b))
    
    # Draw text
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((width // 2, height // 2), "miniZ MCP", fill='white', 
             font=font, anchor='mm')
    
    # Save
    base_dir = Path(__file__).parent
    header_path = base_dir / "installer_header.bmp"
    img.save(str(header_path), format='BMP')
    print(f"✅ Created: {header_path}")
    
    return header_path

if __name__ == "__main__":
    print("🎨 Creating icons and images...")
    create_icon()
    create_installer_banner()
    create_installer_header()
    print("\n✅ All images created!")
