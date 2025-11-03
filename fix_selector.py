#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('xiaozhi_final.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix selector trong saveDevices
old = "const inputs = card.querySelectorAll('input[type=text]');"
new = "const inputs = card.querySelectorAll('input[type=\"text\"]');"

if old in content:
    content = content.replace(old, new)
    with open('xiaozhi_final.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ ĐÃ SỬA - Selector trong saveDevices: input[type=\"text\"]")
else:
    print("❌ Không tìm thấy selector cần sửa")
    print("Tìm kiếm pattern khác...")
    if 'input[type=text]' in content:
        print("✅ Tìm thấy input[type=text] trong file")
        # Thử replace toàn bộ
        content = content.replace('input[type=text]', 'input[type="text"]')
        with open('xiaozhi_final.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ ĐÃ THAY THẾ TẤT CẢ input[type=text]")
