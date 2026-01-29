import asyncio
import websockets
import json

async def test_conn():
    uri = "ws://127.0.0.1:18789"
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            cmd = {"type": "ping", "message": "Hello from Verifier"}
            await websocket.send(json.dumps(cmd))
            print("Message sent.")
            resp = await websocket.recv()
            print(f"Received: {resp}")
    except ConnectionRefusedError:
        print("Failed: Connection Refused. Server might not be running.")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_conn())
