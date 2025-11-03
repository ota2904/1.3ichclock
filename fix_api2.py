with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# Sửa API save_endpoints để nhận Body đúng cách
old_api = """@app.post("/api/endpoints/save")
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
        return {"success": False, "error": str(e)}"""

new_api = """@app.post("/api/endpoints/save")
async def save_endpoints(data: dict):
    global endpoints_config
    try:
        devices = data.get('devices', [])
        if not devices:
            return {"success": False, "error": "Khong co du lieu"}
        
        # Cap nhat endpoints_config
        endpoints_config = []
        for dev in devices:
            endpoints_config.append({
                'name': dev.get('name', 'Device'),
                'token': dev.get('token', ''),
                'enabled': bool(dev.get('token', ''))
            })
        
        return {"success": True, "message": "Da luu " + str(len(devices)) + " thiet bi"}
    except Exception as e:
        return {"success": False, "error": str(e)}"""

content = content.replace(old_api, new_api)

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK 2/2 - Da sua API save_endpoints")
