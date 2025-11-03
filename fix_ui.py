with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# Sửa card.innerHTML trong loadDevices
old_html = """                card.innerHTML = `
                    <h4> ${ep.name}</h4>
                    <input type="text" placeholder="JWT Token" value="${ep.token}" id="token-${i}">
                    <button onclick="switchDevice(${i})"> Chuyen sang thiet bi nay</button>
                `;"""

new_html = """                card.innerHTML = '<h4>Thiet bi ' + (i+1) + '</h4>' +
                    '<input type=\"text\" placeholder=\"Ten thiet bi\" value=\"' + ep.name + '\" style=\"margin-bottom:8px;\">' +
                    '<input type=\"text\" placeholder=\"JWT Token\" value=\"' + ep.token + '\" id=\"token-' + i + '\" style=\"margin-bottom:8px;\">' +
                    '<button onclick=\"switchDevice(' + i + ')\" style=\"margin-top:4px;\">Su dung</button>';"""

content = content.replace(old_html, new_html)

# Thêm nút "Thêm thiết bị"
old_btns = """onclick="loadDevices()"> Tải lại</button>
                    <button style="background:#3b82f6;padding:12px 24px;border:none;border-radius:8px;color:white;cursor:pointer;font-weight:bold;" onclick="saveDevices()"> Lưu cấu hình</button>"""

new_btns = """onclick="loadDevices()"> Tải lại</button>
                    <button style="background:#8b5cf6;padding:12px 24px;border:none;border-radius:8px;color:white;cursor:pointer;font-weight:bold;" onclick="addDevice()"> Thêm</button>
                    <button style="background:#3b82f6;padding:12px 24px;border:none;border-radius:8px;color:white;cursor:pointer;font-weight:bold;" onclick="saveDevices()"> Lưu</button>"""

content = content.replace(old_btns, new_btns)

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK 3/3 - Da sua loadDevices va them nut Add")
