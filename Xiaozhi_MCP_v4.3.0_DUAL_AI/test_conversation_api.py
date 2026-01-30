#!/usr/bin/env python3
"""
Test script cho Conversation History API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("TESTING CONVERSATION HISTORY API")
    print("=" * 60)
    
    # Test 1: Get conversation history
    print("\n1. Testing GET /api/conversation/history")
    try:
        response = requests.get(f"{BASE_URL}/api/conversation/history")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Total messages: {data.get('total_messages')}")
        if data.get('messages'):
            print(f"   First message: {json.dumps(data['messages'][0], indent=2, ensure_ascii=False)}")
        print("   ✅ API hoạt động!")
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
    
    # Test 2: Get recent conversation
    print("\n2. Testing GET /api/conversation/recent/5")
    try:
        response = requests.get(f"{BASE_URL}/api/conversation/recent/5")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Count: {data.get('count')}")
        print("   ✅ API hoạt động!")
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
    
    # Test 3: Add a test message
    print("\n3. Testing POST /api/conversation/add")
    try:
        test_message = {
            "role": "user",
            "content": "Test message from test script",
            "metadata": {"source": "test_script"}
        }
        response = requests.post(
            f"{BASE_URL}/api/conversation/add",
            json=test_message
        )
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Success: {data.get('success')}")
        print(f"   Message: {data.get('message')}")
        print("   ✅ Đã thêm message test!")
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
    
    # Test 4: Check conversation file
    print("\n4. Checking conversation history file")
    try:
        import os
        from pathlib import Path
        
        # Check trong AppData
        appdata = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        conv_dir = Path(appdata) / "miniZ_MCP" / "conversations"
        conv_file = conv_dir / "conversation_history.json"
        
        print(f"   File path: {conv_file}")
        print(f"   Exists: {conv_file.exists()}")
        
        if conv_file.exists():
            with open(conv_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"   Messages in file: {len(data)}")
            print("   ✅ File OK!")
        else:
            print("   ⚠️ File chưa tồn tại (có thể chưa có dữ liệu)")
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETED!")
    print("=" * 60)

if __name__ == "__main__":
    print("\n⚠️ Đảm bảo xiaozhi_final.py đang chạy trên port 8000!")
    input("Press Enter để bắt đầu test...")
    test_api()
