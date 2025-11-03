#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('xiaozhi_final.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Tìm vị trí forEach block (khoảng line 1093-1100)
in_foreach = False
foreach_start = -1
foreach_end = -1

for i, line in enumerate(lines):
    if 'data.endpoints.forEach((ep, i) => {' in line:
        foreach_start = i
        in_foreach = True
    if in_foreach and '});' in line and 'appendChild' in lines[i-1]:
        foreach_end = i
        break

if foreach_start == -1:
    print("❌ Không tìm thấy forEach block")
    exit(1)

print(f"✅ Tìm thấy forEach: dòng {foreach_start+1} - {foreach_end+1}")

# Code mới
new_code = """              data.endpoints.forEach((ep, i) => {
                  const card = document.createElement('div');
                  card.className = 'device-card' + (ep.enabled ? ' active' : '');
                  card.innerHTML = '<h4>📱 Thiet bi ' + (i+1) + '</h4>' +
                      '<input type="text" placeholder="Ten thiet bi" value="' + ep.name + '" style="margin-bottom:8px;">' +
                      '<input type="text" placeholder="JWT Token" value="' + ep.token + '" id="token-' + i + '" style="margin-bottom:8px;">' +
                      '<button onclick="switchDevice(' + i + ')" style="margin-top:4px;background:#10b981;">Su dung thiet bi nay</button>';
                  grid.appendChild(card);
              });
"""

# Thay thế
lines[foreach_start:foreach_end+1] = [new_code]

# Ghi lại
with open('xiaozhi_final.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ ĐÃ SỬA - loadDevices() bây giờ có 2 input (tên + token)")
