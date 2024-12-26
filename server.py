import asyncio
from threading import Thread

import websockets
import json
from functools import partial

from flask import Flask, send_from_directory

app = Flask(__name__)


class RobotServer:
    def __init__(self):
        self._gimbal_backend = {'yaw': 0, 'pitch': 0}
        self._chassis_backend = {'yaw': 0, 'speed': 0}

    async def handle_websocket(self, websocket):
        print(f"Client connected from {websocket.remote_address}")
        try:
            async for message in websocket:
                print(f"Received message: {message}")

                # Parse the JSON message
                payload = json.loads(message)

                # Example: Update backend with received data
                self._gimbal_backend['yaw'] = payload[0]
                self._gimbal_backend['pitch'] = payload[1]
                self._chassis_backend['yaw'] = payload[2]
                self._chassis_backend['speed'] = payload[3]

                # Echo a response (optional)
                response = {"status": "received"}
                await websocket.send(json.dumps(response))
        except websockets.ConnectionClosed as e:
            print(f"Connection closed: {e}")

    async def start(self, host="0.0.0.0", port=9000):
        # Use functools.partial to bind self to handle_websocket
        websocket_handler = partial(self.handle_websocket)
        print(f"Starting WebSocket server on ws://{host}:{port}")
        async with websockets.serve(websocket_handler, host, port):
            await asyncio.Future()  # Run forever


@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)


def start_flask():
    app.run(host='0.0.0.0', port=5000)


if __name__ == "__main__":
    flask_thread = Thread(target=start_flask)
    flask_thread.start()

    server = RobotServer()
    asyncio.run(server.start())
