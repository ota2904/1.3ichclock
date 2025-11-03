"""
Debug WebSocket MCP connection
"""
import asyncio
import websockets
import json

async def debug_websocket():
    uri = "ws://localhost:8000/ws"

    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Send initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {}
            }
            print(f"📤 Sending: {init_msg}")
            await websocket.send(json.dumps(init_msg))

            # Receive response
            response = await websocket.recv()
            print(f"📥 Received: {response}")

            # Send tools/list
            list_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            print(f"📤 Sending tools/list...")
            await websocket.send(json.dumps(list_msg))

            # Receive response
            response = await websocket.recv()
            tools_data = json.loads(response)
            tools = tools_data.get("result", {}).get("tools", [])
            print(f"📋 Found {len(tools)} tools")

            website_tools = [t["name"] for t in tools if t["name"].startswith("open_")]
            print(f"🌐 Website tools: {website_tools}")

            # Try calling open_youtube
            if "open_youtube" in [t["name"] for t in tools]:
                call_msg = {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "open_youtube",
                        "arguments": {"search_query": "debug test"}
                    }
                }
                print(f"📤 Calling open_youtube...")
                await websocket.send(json.dumps(call_msg))

                # Receive response
                response = await websocket.recv()
                print(f"📥 Tool result: {response}")

            print("✅ Debug completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_websocket())
