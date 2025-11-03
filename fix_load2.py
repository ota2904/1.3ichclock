with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# Tìm và thay thế phần card.innerHTML trong loadDevices
old_card = """              data.endpoints.forEach((ep, i) => {
                  const card = document.createElement('div');
                  card.className = 'device-card' + (ep.enabled ? ' active' : '');
                  card.innerHTML = `
                      <h4> ${ep.name}</h4>
                      <input type="text" placeholder="JWT Token" value="${ep.token}" id="token-${i}">
                      <button onclick="switchDevice(${i})"> Chuyển sang thiết bị này</button>
                  `;
                  grid.appendChild(card);
              });"""

new_card = """              data.endpoints.forEach((ep, i) => {
                  const card = document.createElement('div');
                  card.className = 'device-card' + (ep.enabled ? ' active' : '');
                  card.innerHTML = '<h4>Thiet bi ' + (i+1) + '</h4>' +
                      '<input type=\"text\" placeholder=\"Ten thiet bi\" value=\"' + ep.name + '\" style=\"margin-bottom:8px;\">' +
                      '<input type=\"text\" placeholder=\"JWT Token\" value=\"' + ep.token + '\" id=\"token-' + i + '\" style=\"margin-bottom:8px;\">' +
                      '<button onclick=\"switchDevice(' + i + ')\" style=\"margin-top:4px;background:#10b981;\">Su dung thiet bi nay</button>';
                  grid.appendChild(card);
              });"""

content = content.replace(old_card, new_card)

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK 1/2 - Da sua loadDevices card.innerHTML")
