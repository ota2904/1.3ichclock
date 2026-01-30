"""
Test VLC MCP System - Hybrid Architecture
"""
import asyncio
import json

async def test_mcp_protocol():
    """Test MCP JSON-RPC 2.0 protocol"""
    print("=" * 70)
    print("🧪 TEST VLC MCP SYSTEM - HYBRID ARCHITECTURE")
    print("=" * 70)
    
    # Import modules
    try:
        from vlc_mcp_server import VLCMCPServer
        from vlc_tools_registry import VLC_TOOLS_REGISTRY, get_all_tools_for_gemini
        print("\n✅ Modules imported successfully")
    except Exception as e:
        print(f"\n❌ Import error: {e}")
        return
    
    # Test 1: Tools Registry
    print(f"\n📚 [Test 1] Tools Registry")
    print(f"   Total tools: {len(VLC_TOOLS_REGISTRY)}")
    print(f"   Tools: {', '.join(VLC_TOOLS_REGISTRY.keys())}")
    
    # Test 2: Gemini Format Conversion
    print(f"\n🤖 [Test 2] Gemini Format Conversion")
    gemini_tools = get_all_tools_for_gemini()
    print(f"   Total Gemini tools: {len(gemini_tools)}")
    print(f"   Sample tool:")
    if gemini_tools:
        print(f"   {json.dumps(gemini_tools[0], indent=4)}")
    
    # Test 3: Mock VLC Player
    print(f"\n🎵 [Test 3] Mock VLC Player")
    
    class MockVLCPlayer:
        def __init__(self):
            self._playing = False
            self._volume = 50
            self._position = 0.0
        
        def play(self):
            self._playing = True
            return True
        
        def pause(self):
            self._playing = False
            return True
        
        def stop(self):
            self._playing = False
            return True
        
        def next(self):
            print("   [Mock] Next track")
            return True
        
        def previous(self):
            print("   [Mock] Previous track")
            return True
        
        def is_playing(self):
            return self._playing
        
        def audio_set_volume(self, vol):
            self._volume = vol
        
        def audio_get_volume(self):
            return self._volume
        
        def set_position(self, pos):
            self._position = pos
        
        def get_position(self):
            return self._position
        
        def get_time(self):
            return 12000  # 12 seconds
        
        def get_length(self):
            return 180000  # 3 minutes
        
        def get_state(self):
            return 3 if self._playing else 4  # 3=playing, 4=paused
        
        def get_media(self):
            return None
    
    mock_player = MockVLCPlayer()
    print(f"   ✅ Mock player created")
    
    # Test 4: MCP Server Initialization
    print(f"\n🚀 [Test 4] MCP Server Initialization")
    try:
        mcp_server = VLCMCPServer(mock_player)
        print(f"   ✅ MCP Server created")
        print(f"   Registered tools: {len(mcp_server.tools)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Test 5: List Tools Request
    print(f"\n📋 [Test 5] List Tools Request")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    response = await mcp_server.handle_mcp_request(request)
    print(f"   Request: {json.dumps(request, indent=2)}")
    print(f"   Response: {json.dumps(response, indent=2)[:500]}...")
    
    # Test 6: Play Command
    print(f"\n▶️ [Test 6] Play Command via MCP")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "vlc.play",
            "arguments": {}
        },
        "id": 2
    }
    response = await mcp_server.handle_mcp_request(request)
    print(f"   Request: {json.dumps(request, indent=2)}")
    print(f"   Response: {json.dumps(response, indent=2)}")
    print(f"   Is playing? {mock_player.is_playing()}")
    
    # Test 7: Set Volume
    print(f"\n🔊 [Test 7] Set Volume to 80")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "vlc.set_volume",
            "arguments": {"volume": 80}
        },
        "id": 3
    }
    response = await mcp_server.handle_mcp_request(request)
    print(f"   Request: {json.dumps(request, indent=2)}")
    print(f"   Response: {json.dumps(response, indent=2)}")
    print(f"   Current volume: {mock_player.audio_get_volume()}")
    
    # Test 8: Get Status
    print(f"\n📊 [Test 8] Get Status")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "vlc.get_status",
            "arguments": {}
        },
        "id": 4
    }
    response = await mcp_server.handle_mcp_request(request)
    print(f"   Request: {json.dumps(request, indent=2)}")
    print(f"   Response: {json.dumps(response, indent=2)}")
    
    # Test 9: Invalid Tool
    print(f"\n❌ [Test 9] Invalid Tool (Error Handling)")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "vlc.invalid_tool",
            "arguments": {}
        },
        "id": 5
    }
    response = await mcp_server.handle_mcp_request(request)
    print(f"   Request: {json.dumps(request, indent=2)}")
    print(f"   Response: {json.dumps(response, indent=2)}")
    
    # Test 10: Invalid Parameters
    print(f"\n⚠️ [Test 10] Invalid Parameters (Validation)")
    request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "vlc.set_volume",
            "arguments": {"volume": 150}  # > 100, invalid
        },
        "id": 6
    }
    response = await mcp_server.handle_mcp_request(request)
    print(f"   Request: {json.dumps(request, indent=2)}")
    print(f"   Response: {json.dumps(response, indent=2)}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_mcp_protocol())
