import asyncio
from threading import Thread

import websockets
import json
from functools import partial

from flask import Flask, send_from_directory

from backend.common.utilities import is_raspberry_pi, remap
from backend.hardware_backends.chassis_backend import DummyChassisBackend, PCA9685CarChassis
from backend.hardware_backends.gimbal_backend import DummyGimbalBackend, PCA9685GimbalBackend
from backend.hardware_backends.pi_hats import PCA9685

app = Flask(__name__)


class RobotServer:
    def __init__(self):
        self._hat = None  # Optional Raspberry Pi hats
        self._gimbal_backend = None
        self._chassis_backend = None
        self._initialize_backend()

    def _initialize_backend(self):
        if is_raspberry_pi():  # assuming ARM is Raspberry Pi
            print("Raspberry Pi detected. Using real hardware.")
            self._clear_screen_command = 'clear'
            self._hat = PCA9685()
            self._gimbal_backend = PCA9685GimbalBackend(self._hat)
            self._chassis_backend = PCA9685CarChassis(self._hat)
            self._fail_safe_mode()
        else:
            print("Unknown hardware platform. Running dummy hardware.")
            self._clear_screen_command = 'cls'
            self._gimbal_backend = DummyGimbalBackend()
            self._chassis_backend = DummyChassisBackend()

    def _fail_safe_mode(self):
        self._gimbal_backend.yaw = 0
        self._gimbal_backend.pitch = 0
        self._chassis_backend.yaw = 0
        self._chassis_backend.speed = 0

    async def handle_websocket(self, websocket):
        print(f"Client connected from {websocket.remote_address}")
        try:
            async for message in websocket:
                print(f"Received message: {message}")

                # Parse the JSON message
                payload = json.loads(message)

                # Example: Update backend with received data
                self._gimbal_backend.yaw = payload[0]
                self._gimbal_backend.pitch = payload[1]
                self._chassis_backend.yaw = payload[2]
                speed = payload[3]
                if speed < -0.1:
                    self._chassis_backend.speed = remap(speed, -1, 0, -1, -0.25)
                elif speed > 0.1:
                    self._chassis_backend.speed = remap(speed, 0, 1, 0.25, 1)
                else:
                    self._chassis_backend.speed =0

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
