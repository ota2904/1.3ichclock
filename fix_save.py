with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_save_func = """        async function saveDevices() {
            addLog('Dang luu...', 'info');
            const devices = [];
            document.querySelectorAll('.device-card').forEach((card, i) => {
                const inputs = card.querySelectorAll('input[type=text]');
                devices.push({
                    name: inputs[0] ? inputs[0].value : 'Thiet bi ' + (i+1),
                    token: inputs[1] ? inputs[1].value : '',
                    enabled: inputs[1] && inputs[1].value.length > 0
                });
            });
            try {
                const response = await fetch('/api/endpoints/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({devices: devices})
                });
                const data = await response.json();
                if (data.success) {
                    addLog('Da luu!', 'success');
                    loadDevices();
                }
            } catch (error) {
                addLog('Loi: ' + error.message, 'error');
            }
        }
""".split('\n')

new_lines = [line + '\n' for line in new_save_func]
new_content = lines[:1119] + new_lines + lines[1122:]

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.writelines(new_content)

print("OK 1/2")
