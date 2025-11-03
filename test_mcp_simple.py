"""
Simple MCP test - just connect and list tools
"""
import asyncio
import websockets
import json

async def simple_test():
    try:
        uri = "ws://localhost:8000/ws"
        print("🔌 Connecting to MCP...")

        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {}
            }
            await websocket.send(json.dumps(init_msg))
            response = await websocket.recv()
            print(f"📨 Init response: {json.loads(response)}")

            # List tools
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

            print(f"📋 Found {len(tools)} tools")

            # Check website tools
            website_tools = [t["name"] for t in tools if t["name"].startswith("open_")]
            print(f"🌐 Website tools: {website_tools}")

            print("✅ MCP test completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
