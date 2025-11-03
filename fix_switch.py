with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# Sửa API switch để trả về JSON thay vì raise Exception
old_switch = """@app.post("/api/endpoints/switch/{index}")
async def switch_endpoint(index: int):
    global active_endpoint_index
    if 0 <= index < len(endpoints_config):
        if endpoints_config[index]["token"]:
            active_endpoint_index = index
            return {"success": True, "message": f"Đã chuyển sang {endpoints_config[index]['name']}"}
        raise HTTPException(400, "Token is empty")
    raise HTTPException(404, "Invalid device index")"""

new_switch = """@app.post("/api/endpoints/switch/{index}")
async def switch_endpoint(index: int):
    global active_endpoint_index
    if index < 0 or index >= len(endpoints_config):
        return {"success": False, "error": "Thiet bi khong ton tai"}
    
    device = endpoints_config[index]
    if not device.get("token"):
        return {"success": False, "error": "Thiet bi chua co token. Hay nhap token va luu lai!"}
    
    active_endpoint_index = index
    return {"success": True, "message": f"Da chuyen sang {device['name']}"}"""

content = content.replace(old_switch, new_switch)

with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(content)

print("OK 3/3 - Da sua API switch_endpoint")
