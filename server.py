import argparse
import socket
import os
from threading import Thread

import websockets
import asyncio

from backend.hardware_backends.chassis_backend import PCA9685CarChassis, DummyChassisBackend
from backend.hardware_backends.gimbal_backend import PCA9685GimbalBackend, DummyGimbalBackend
from backend.common.server_packet import ControllerPacket
from backend.common.utilities import *
from backend.hardware_backends.pi_hats import PCA9685


class RobotServer:
    def _fail_safe_mode(self):
        self._chassis_backend.speed = 0

    def _handle_connection(self):
        while True:
            if self._client_socket is None:
                self._client_socket, self._client_address = self._socket.accept()

            data_received = self._client_socket.recv(ControllerPacket.size())
            if data_received:
                try:
                    packet = ControllerPacket(data_received)
                    self._client_socket.send(data_received)
                    self._gimbal_backend.yaw = packet.camera_yaw
                    self._gimbal_backend.pitch = packet.camera_pitch
                    self._chassis_backend.yaw = packet.robot_yaw
                    self._chassis_backend.speed = packet.robot_speed
                except Exception as e:
                    print("Data transmission error: " + e.__str__())
                    self._fail_safe_mode()
            else:
                self._fail_safe_mode()

    async def _handle_websocket(self, websocket, path):
        while True:
            import json
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                print("< {}".format(data))

                payload = json.loads(data)

                self._gimbal_backend.yaw = payload[0]
                self._gimbal_backend.pitch = payload[1]
                self._chassis_backend.yaw = payload[2]
                self._chassis_backend.speed = payload[3]
            except asyncio.TimeoutError:
                self._fail_safe_mode()

    def _clear_screen(self):
        os.system(self._clear_screen_command)

    def _initialize_backend(self):
        if is_raspberry_pi():  # assuming ARM is Raspberry Pi
            self._clear_screen_command = 'clear'
            self._hat = PCA9685()
            self._gimbal_backend = PCA9685GimbalBackend(self._hat)
            self._chassis_backend = PCA9685CarChassis(self._hat)
        else:
            self._clear_screen_command = 'cls'
            self._gimbal_backend = DummyGimbalBackend()
            self._chassis_backend = DummyChassisBackend()

    async def start_websocket_server(self, host, wsport):
        start_server = websockets.serve(self._handle_websocket, host, wsport)
        await start_server

    def start(self, host, wsport):
        # Start the WebSocket server in an async context
        asyncio.run(self.start_websocket_server(host, wsport))
        print(f"Listening on websocket port {wsport}")

    def __init__(self, host: str, port: int, wsport: int):
        self._hat = None  # Optional Raspberry Pi hats
        self._initialize_backend()

        # This is to handle python client controls
        self._client_socket = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, port))
        self._socket.listen(1)
        print(f"Listening on socket port {port}")

        self._updater = Thread(target=self._handle_connection)
        self._updater.start()

        # For the web browser websockets controls
        self.start(host, wsport)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect to the robot and send control commands.')
    parser.add_argument('host', metavar='host', type=str, help='server IP or hostname')
    parser.add_argument('port', metavar='port', type=int, help='server port')
    parser.add_argument('wsport', metavar='wsport', type=int, help='websocket server port')
    args = parser.parse_args()

    server = RobotServer(args.host, args.port, args.wsport)
