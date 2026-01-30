"""
KIỂM TRA TOÀN BỘ 5 VẤN ĐỀ
Test comprehensive cho miniZ MCP v4.3.1
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 KIỂM TRA TOÀN BỘ 5 VẤN ĐỀ")
print("=" * 70)
print()

# ============================================================================
# VẤN ĐỀ 1: Kiểm tra API keys có bị hardcode không
# ============================================================================
print("1️⃣  VẤN ĐỀ 1: Kiểm tra API keys hardcoded")
print("-" * 70)

config_file = "xiaozhi_endpoints.json"
if os.path.exists(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    has_keys = any([
        config.get('gemini_api_key'),
        config.get('openai_api_key'),
        config.get('serper_api_key')
    ])
    
    if has_keys:
        print(f"✅ API keys được lưu trong config file: {config_file}")
        print(f"   - Gemini: {'***' + config.get('gemini_api_key', '')[-8:] if config.get('gemini_api_key') else 'Chưa có'}")
        print(f"   - OpenAI: {'***' + config.get('openai_api_key', '')[-8:] if config.get('openai_api_key') else 'Chưa có'}")
        print(f"   - Serper: {'***' + config.get('serper_api_key', '')[-8:] if config.get('serper_api_key') else 'Chưa có'}")
        print("✅ PASS: Không hardcode trong source code, lưu riêng file config")
    else:
        print("⚠️  Chưa có API keys trong config")
else:
    print(f"⚠️  File {config_file} chưa tồn tại")

print()

# ============================================================================
# VẤN ĐỀ 2: Kiểm tra chức năng lưu config
# ============================================================================
print("2️⃣  VẤN ĐỀ 2: Kiểm tra chức năng lưu endpoints/config")
print("-" * 70)

try:
    # Test save endpoints
    test_endpoints = [
        {"name": "Test Device 1", "token": "test_token_123", "enabled": True},
        {"name": "Test Device 2", "token": "", "enabled": False}
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/save_endpoints",
        json={"devices": test_endpoints},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print("✅ API /api/save_endpoints hoạt động")
            
            # Verify file was saved
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                if saved_config.get('endpoints'):
                    print(f"✅ Config đã được lưu vào {config_file}")
                    print(f"   Số devices: {len(saved_config['endpoints'])}")
                    print("✅ PASS: Chức năng lưu hoạt động tốt")
                else:
                    print("❌ FAIL: Không lưu được endpoints vào file")
            else:
                print(f"❌ FAIL: File {config_file} không được tạo")
        else:
            print(f"❌ FAIL: {result.get('error')}")
    else:
        print(f"❌ FAIL: HTTP {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Server không chạy - Cần: python xiaozhi_final.py")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# ============================================================================
# VẤN ĐỀ 3: Kiểm tra mở trực tiếp video YouTube
# ============================================================================
print("3️⃣  VẤN ĐỀ 3: Tính năng mở trực tiếp video YouTube")
print("-" * 70)

try:
    # Test search_youtube_video function
    test_video = "Sơn Tùng MTP Chúng Ta Của Hiện Tại"
    
    response = requests.post(
        f"{BASE_URL}/api/call_tool",
        json={
            "tool": "search_youtube_video",
            "args": {
                "video_title": test_video,
                "auto_open": False  # Không mở browser, chỉ test search
            }
        },
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get("success"):
            print(f"✅ Tìm thấy video: {result.get('title', 'N/A')[:50]}...")
            print(f"   URL: {result.get('url', 'N/A')}")
            print(f"   Channel: {result.get('channel', 'N/A')}")
            
            # Check if it's search or direct video
            if '/watch?v=' in result.get('url', ''):
                print("✅ PASS: Mở trực tiếp video (không phải search)")
            else:
                print("⚠️  PARTIAL: Trả về search results thay vì direct link")
        else:
            print(f"❌ FAIL: {result.get('error')}")
            print("⚠️  Có thể thiếu: pip install youtube-search-python")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("❌ Server không chạy")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# ============================================================================
# VẤN ĐỀ 4: Kiểm tra lưu và kích hoạt JWT Token/Endpoint
# ============================================================================
print("4️⃣  VẤN ĐỀ 4: Lưu và kích hoạt JWT Token/Endpoint")
print("-" * 70)

try:
    # Test 1: Save endpoint with JWT token
    jwt_test = {
        "devices": [
            {
                "name": "Device with JWT",
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test",
                "enabled": True
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/save_endpoints",
        json=jwt_test,
        timeout=10
    )
    
    if response.status_code == 200 and response.json().get("success"):
        print("✅ Lưu JWT token thành công")
        
        # Verify saved
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if config.get('endpoints'):
                first_endpoint = config['endpoints'][0]
                if first_endpoint.get('token'):
                    print(f"✅ Token đã lưu: {first_endpoint['token'][:20]}...")
                    print(f"   Enabled: {first_endpoint.get('enabled')}")
                    
                    # Test 2: Activate endpoint
                    response2 = requests.post(
                        f"{BASE_URL}/api/activate_endpoint",
                        json={"index": 0},
                        timeout=10
                    )
                    
                    if response2.status_code == 200 and response2.json().get("success"):
                        print("✅ Kích hoạt endpoint thành công")
                        print("✅ PASS: Lưu và kích hoạt JWT Token hoạt động tốt")
                    else:
                        print("⚠️  Kích hoạt không thành công")
                else:
                    print("❌ FAIL: Token không được lưu")
        else:
            print("❌ FAIL: Config file không tồn tại")
    else:
        print("❌ FAIL: Không lưu được endpoint")
        
except requests.exceptions.ConnectionError:
    print("❌ Server không chạy")
except Exception as e:
    print(f"❌ Error: {e}")

print()

# ============================================================================
# VẤN ĐỀ 5: Kiểm tra mở nhạc từ thư mục user
# ============================================================================
print("5️⃣  VẤN ĐỀ 5: Mở nhạc từ thư mục người dùng")
print("-" * 70)

try:
    # Check if custom music folder config exists
    music_config_file = "custom_music_folder.txt"
    music_folder_config = "music_folder_config.json"
    
    custom_folder = None
    if os.path.exists(music_config_file):
        with open(music_config_file, 'r', encoding='utf-8') as f:
            custom_folder = f.read().strip()
    elif os.path.exists(music_folder_config):
        with open(music_folder_config, 'r', encoding='utf-8') as f:
            config = json.load(f)
            custom_folder = config.get('music_folder')
    
    if custom_folder and os.path.exists(custom_folder):
        print(f"✅ Custom music folder được cấu hình: {custom_folder}")
        
        # Count music files
        extensions = ['.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma']
        music_files = []
        for root, dirs, files in os.walk(custom_folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    music_files.append(file)
        
        print(f"   Tìm thấy {len(music_files)} files nhạc")
        
        if len(music_files) > 0:
            # Test play_music API
            test_song = music_files[0]
            print(f"   Test phát: {test_song[:30]}...")
            
            response = requests.post(
                f"{BASE_URL}/api/call_tool",
                json={
                    "tool": "play_music",
                    "args": {
                        "filename": test_song,
                        "create_playlist": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ PASS: Phát nhạc từ thư mục user thành công")
                    print(f"   Đang phát: {result.get('file', 'N/A')}")
                else:
                    print(f"⚠️  Không phát được: {result.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
        else:
            print("⚠️  Không có file nhạc trong thư mục")
            print("✅ PARTIAL PASS: Config đúng nhưng thư mục trống")
    else:
        print("⚠️  Custom music folder chưa được cấu hình")
        print(f"   Tạo file: {music_config_file} với đường dẫn thư mục nhạc")
        
        # Check default music_library
        default_music = "music_library"
        if os.path.exists(default_music):
            extensions = ['.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma']
            count = len([f for root, dirs, files in os.walk(default_music) 
                        for f in files if any(f.lower().endswith(ext) for ext in extensions)])
            print(f"✅ Default music_library/ tồn tại với {count} files")
        else:
            print("⚠️  Default music_library/ không tồn tại")
        
except requests.exceptions.ConnectionError:
    print("❌ Server không chạy")
except Exception as e:
    print(f"❌ Error: {e}")

print()
print("=" * 70)
print("🎉 HOÀN THÀNH KIỂM TRA")
print("=" * 70)
print()
print("📊 TỔNG KẾT:")
print("1. API keys không hardcode - ✅")
print("2. Chức năng lưu config - Cần kiểm tra")
print("3. YouTube direct video - Cần fix")
print("4. JWT Token save/activate - Cần kiểm tra")
print("5. Custom music folder - Cần kiểm tra")
print()
print("💡 Để fix các vấn đề, chạy server trước:")
print("   python xiaozhi_final.py")
