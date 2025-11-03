"""
Test MCP connection and website tools
"""
import asyncio
import websockets
import json

async def test_mcp():
    uri = "ws://localhost:8000/ws"

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to MCP server")

            # Test initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {}
            }
            await websocket.send(json.dumps(init_msg))
            response = await websocket.recv()
            print(f"📨 Initialize response: {json.loads(response)}")

            # Test tools/list
            list_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            await websocket.send(json.dumps(list_msg))
            response = await websocket.recv()
            tools_data = json.loads(response)
            tools = tools_data.get("result", {}).get("tools", [])

            print(f"📋 Total tools: {len(tools)}")

            # Check for website tools
            website_tools = [t for t in tools if t["name"].startswith("open_")]
            print(f"🌐 Website tools found: {len(website_tools)}")
            for tool in website_tools:
                print(f"   - {tool['name']}: {tool['description'][:50]}...")

            # Test open_youtube tool
            if any(t["name"] == "open_youtube" for t in tools):
                print("\n🧪 Testing open_youtube tool...")
                call_msg = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "open_youtube",
                        "arguments": {"search_query": "test"}
                    }
                }
                await websocket.send(json.dumps(call_msg))
                response = await websocket.recv()
                result = json.loads(response)
                print(f"✅ open_youtube result: {result}")

            # Test open_facebook tool
            if any(t["name"] == "open_facebook" for t in tools):
                print("\n🧪 Testing open_facebook tool...")
                call_msg = {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "open_facebook",
                        "arguments": {}
                    }
                }
                await websocket.send(json.dumps(call_msg))
                response = await websocket.recv()
                result = json.loads(response)
                print(f"✅ open_facebook result: {result}")

    except Exception as e:
        print(f"❌ MCP test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp())
