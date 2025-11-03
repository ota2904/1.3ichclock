with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# Sửa switchDevice JavaScript
old_switch_js = """        async function switchDevice(index) {
            const response = await fetch(`/api/endpoints/switch/${index}`, {method: 'POST'});
            const data = await response.json();
            addLog(` ${data.message}`, 'success');
            loadDevices();
        }"""

new_switch_js = """        async function switchDevice(index) {
            try {
                const response = await fetch('/api/endpoints/switch/' + index, {method: 'POST'});
                const data = await response.json();
                if (data.success) {
                    addLog(' ' + data.message, 'success');
                    loadDevices();
                } else {
                    addLog(' ' + data.error, 'error');
                }
            } catch (error) {
                addLog(' Loi: ' + error.message, 'error');
            }
        }"""

content = content.replace(old_switch_js, new_switch_js)

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK 4/4 - Da sua switchDevice JavaScript")
