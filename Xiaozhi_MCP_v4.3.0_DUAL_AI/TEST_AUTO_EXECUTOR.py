"""
🤖 AUTO TOOL EXECUTOR - Test Script
Test tự động phát hiện intent và thực thi tool
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auto_execute(llm_response, original_query="", auto_execute=True):
    """Test API auto_execute"""
    print(f"\n{'='*70}")
    print(f"🧪 TEST: Auto Execute")
    print(f"{'='*70}")
    print(f"📝 LLM Response: {llm_response}")
    print(f"📝 Original Query: {original_query}")
    print(f"⚙️  Auto Execute: {auto_execute}")
    print(f"{'-'*70}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auto_execute",
            json={
                "llm_response": llm_response,
                "original_query": original_query,
                "auto_execute": auto_execute
            },
            timeout=10
        )
        
        result = response.json()
        
        # Display results
        print(f"✅ Status: {response.status_code}")
        print(f"🎯 Intent Detected: {result.get('intent_detected', 'unknown')}")
        print(f"🔧 Tool Suggested: {result.get('tool_suggested', 'none')}")
        print(f"📊 Confidence: {result.get('confidence', 0.0):.2f}")
        print(f"⚡ Tool Executed: {result.get('tool_executed', False)}")
        
        if result.get('tool_result'):
            print(f"\n📦 Tool Result:")
            tool_result = result['tool_result']
            print(f"   Success: {tool_result.get('success', False)}")
            print(f"   Message: {tool_result.get('message', 'N/A')}")
            
            # Display additional details
            for key, value in tool_result.items():
                if key not in ['success', 'message', 'llm_note']:
                    print(f"   {key}: {value}")
        
        print(f"\n💬 Message: {result.get('message', 'N/A')}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: {e}")
        return None


def test_vlc_controls():
    """Test VLC music controls detection"""
    print(f"\n{'#'*70}")
    print(f"🎵 TEST GROUP: VLC MUSIC CONTROLS")
    print(f"{'#'*70}")
    
    test_cases = [
        {
            "llm_response": "OK, đã chuyển bài tiếp theo",
            "original_query": "bài tiếp",
            "expected_tool": "music_next"
        },
        {
            "llm_response": "Đã quay lại bài trước rồi nhé",
            "original_query": "quay lại bài trước",
            "expected_tool": "music_previous"
        },
        {
            "llm_response": "Tạm dừng nhạc rồi",
            "original_query": "tạm dừng",
            "expected_tool": "pause_music"
        },
        {
            "llm_response": "OK, tiếp tục phát nhé",
            "original_query": "tiếp tục",
            "expected_tool": "resume_music"
        },
        {
            "llm_response": "Đã dừng nhạc",
            "original_query": "dừng nhạc",
            "expected_tool": "stop_music"
        }
    ]
    
    results = []
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"Test Case {i}/{len(test_cases)}: {test['expected_tool']}")
        
        result = test_auto_execute(
            llm_response=test['llm_response'],
            original_query=test['original_query'],
            auto_execute=True
        )
        
        # Verify
        if result:
            detected = result.get('tool_suggested')
            expected = test['expected_tool']
            
            if detected == expected:
                print(f"✅ PASS: Detected '{detected}' as expected")
                results.append(True)
            else:
                print(f"❌ FAIL: Expected '{expected}', got '{detected}'")
                results.append(False)
        else:
            print(f"❌ FAIL: No result returned")
            results.append(False)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 SUMMARY: VLC Controls")
    print(f"{'='*70}")
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"❌ Failed: {total - passed}/{total}")
    

def test_detection_only():
    """Test detection without execution"""
    print(f"\n{'#'*70}")
    print(f"🔍 TEST GROUP: DETECTION ONLY (No Execution)")
    print(f"{'#'*70}")
    
    test_cases = [
        "OK, đã next bài",
        "Quay lại bài trước nhé",
        "Pause tạm thời"
    ]
    
    for llm_response in test_cases:
        result = test_auto_execute(
            llm_response=llm_response,
            auto_execute=False  # Chỉ detect, không execute
        )
        
        if result and not result.get('tool_executed'):
            print(f"✅ PASS: Detection only, no execution")
        else:
            print(f"❌ FAIL: Tool was executed unexpectedly")


def test_confidence_threshold():
    """Test confidence threshold"""
    print(f"\n{'#'*70}")
    print(f"📊 TEST GROUP: CONFIDENCE THRESHOLD")
    print(f"{'#'*70}")
    
    # Low confidence - không rõ ràng
    low_confidence_cases = [
        "Có thể làm gì đó với nhạc",
        "Nhạc đang phát",
        "Cảm ơn"
    ]
    
    for llm_response in low_confidence_cases:
        print(f"\n{'─'*70}")
        print(f"Testing: '{llm_response}'")
        
        result = test_auto_execute(
            llm_response=llm_response,
            auto_execute=True
        )
        
        if result:
            confidence = result.get('confidence', 0)
            tool_executed = result.get('tool_executed', False)
            
            if confidence < 0.6:
                if not tool_executed:
                    print(f"✅ PASS: Low confidence ({confidence:.2f}), correctly skipped execution")
                else:
                    print(f"❌ FAIL: Low confidence ({confidence:.2f}), should not execute")
            else:
                print(f"⚠️  WARNING: Confidence {confidence:.2f} is higher than expected")


def test_websocket_integration():
    """Test WebSocket integration (manual check)"""
    print(f"\n{'#'*70}")
    print(f"🌐 WEBSOCKET INTEGRATION TEST")
    print(f"{'#'*70}")
    print(f"""
📝 Manual Test Steps:

1. Mở Web UI: http://localhost:8000
2. Mở Developer Console (F12)
3. Paste code sau vào Console:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {{
  console.log('✅ WebSocket connected');
  
  // Test auto-execute
  ws.send(JSON.stringify({{
    type: 'llm_response_check',
    response: 'OK, đã chuyển bài tiếp theo',
    query: 'bài tiếp',
    auto_execute: true
  }}));
}};

ws.onmessage = (event) => {{
  const data = JSON.parse(event.data);
  if (data.type === 'auto_execute_result') {{
    console.log('🎯 Auto Execute Result:', data);
  }}
}};
```

4. Kiểm tra Console output
5. Verify tool được thực thi
""")


def main():
    """Main test runner"""
    print(f"""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║     🤖 AUTO TOOL EXECUTOR - TEST SUITE                     ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    # Check server availability
    try:
        response = requests.get(f"{BASE_URL}/api/vlc_status", timeout=5)
        print(f"✅ Server is running at {BASE_URL}")
    except requests.exceptions.RequestException:
        print(f"❌ ERROR: Server not running at {BASE_URL}")
        print(f"   Please start the server first: python xiaozhi_final.py")
        return
    
    # Run test groups
    try:
        test_vlc_controls()
        test_detection_only()
        test_confidence_threshold()
        test_websocket_integration()
        
        print(f"\n{'='*70}")
        print(f"✅ ALL TESTS COMPLETED")
        print(f"{'='*70}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
