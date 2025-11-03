import re

# Đọc file
with open("xiaozhi_final.py", "r", encoding="utf-8") as f:
    content = f.read()

# Tìm vị trí chèn (sau calculator, trước endpoints)
target = '@app.get("/api/endpoints")'
insert_pos = content.find(target)

if insert_pos == -1:
    print(" Không tìm thấy vị trí chèn")
    exit(1)

# 23 API endpoints mới
new_apis = """
# ===== 23 API ENDPOINTS MỚI (Tool 8-30) =====

@app.post("/api/tool/open_application")
async def api_open_app(data: dict):
    result = await open_application(data.get("app_name", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/list_running_processes")
async def api_list_procs(data: dict):
    result = await list_running_processes(data.get("limit", 10))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/kill_process")
async def api_kill_proc(data: dict):
    result = await kill_process(data.get("identifier", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/create_file")
async def api_create_file(data: dict):
    result = await create_file(data.get("path", ""), data.get("content", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/read_file")
async def api_read_file(data: dict):
    result = await read_file(data.get("path", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/list_files")
async def api_list_files(data: dict):
    result = await list_files(data.get("directory", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_disk_usage")
async def api_disk_usage():
    result = await get_disk_usage()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_network_info")
async def api_network():
    result = await get_network_info()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_battery_status")
async def api_battery():
    result = await get_battery_status()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/search_web")
async def api_search(data: dict):
    result = await search_web(data.get("query", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/get_clipboard")
async def api_get_clip():
    result = await get_clipboard()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_clipboard")
async def api_set_clip(data: dict):
    result = await set_clipboard(data.get("text", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/play_sound")
async def api_sound(data: dict):
    result = await play_sound(data.get("frequency", 1000), data.get("duration", 500))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_brightness")
async def api_brightness(data: dict):
    result = await set_brightness(data.get("level", 50))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/minimize_all_windows")
async def api_minimize():
    result = await minimize_all_windows()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/undo_action")
async def api_undo():
    result = await undo_action()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/toggle_dark_mode")
async def api_theme():
    result = await toggle_dark_mode()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/set_wallpaper")
async def api_wallpaper(data: dict):
    result = await set_wallpaper(data.get("path", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/paste_text")
async def api_paste():
    result = await paste_text()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/press_enter")
async def api_enter():
    result = await press_enter()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/find_on_screen")
async def api_find(data: dict):
    result = await find_on_screen(data.get("text", ""))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/lock_computer")
async def api_lock():
    result = await lock_computer()
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

@app.post("/api/tool/shutdown_computer")
async def api_shutdown(data: dict):
    result = await shutdown_computer(data.get("delay", 0))
    if not result["success"]:
        raise HTTPException(500, result["error"])
    return result

"""

# Chèn vào
new_content = content[:insert_pos] + new_apis + "\n" + content[insert_pos:]

# Lưu lại
with open("xiaozhi_final.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print(" Đã thêm 23 API endpoints mới!")
print(" Tổng endpoints: 7 cũ + 23 mới = 30 endpoints")
print(" File đã được cập nhật: xiaozhi_final.py")
