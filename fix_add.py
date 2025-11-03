with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Thêm function addDevice() sau saveDevices
marker = """        async function saveDevices() {"""
pos = content.find(marker)
end_pos = content.find("        function addLog", pos)

add_func = """
        function addDevice() {
            const grid = document.getElementById('device-grid');
            const newIndex = grid.children.length;
            const card = document.createElement('div');
            card.className = 'device-card';
            card.innerHTML = '<h4>Thiet bi ' + (newIndex + 1) + '</h4>' +
                '<input type=\"text\" placeholder=\"Ten thiet bi\" value=\"Thiet bi ' + (newIndex + 1) + '\" style=\"margin-bottom:8px;\">' +
                '<input type=\"text\" placeholder=\"JWT Token\" value=\"\" style=\"margin-bottom:8px;\">' +
                '<button onclick=\"this.parentElement.remove()\" style=\"background:#ef4444;\">Xoa</button>';
            grid.appendChild(card);
            addLog('Da them thiet bi moi!', 'success');
        }

"""

content = content[:end_pos] + add_func + content[end_pos:]

# 2. Thêm API endpoint /api/endpoints/save
api_marker = "@app.post(\"/api/endpoints/switch/{index}\")"
api_pos = content.find(api_marker)
api_end = content.find("\n@app.websocket", api_pos)

save_api = """
@app.post("/api/endpoints/save")
async def save_endpoints(request: dict):
    global endpoints_config
    try:
        devices = request.get('devices', [])
        # Cap nhat endpoints_config
        endpoints_config = []
        for dev in devices:
            endpoints_config.append({
                'name': dev.get('name', 'Device'),
                'token': dev.get('token', ''),
                'enabled': dev.get('enabled', False)
            })
        return {"success": True, "message": "Da luu cau hinh"}
    except Exception as e:
        return {"success": False, "error": str(e)}

"""

content = content[:api_end] + save_api + content[api_end:]

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK 2/2 - Da them addDevice() va API /api/endpoints/save")
