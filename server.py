import argparse
import socket
from threading import Thread

from hardware_backends.gimbal_backend import SG90ServoGimbalBackend, DummyGimbalBackend
from server_packet import ControllerPacket
from utilities import *


class RobotServer:
    def _fail_safe_mode(self):
        # Todo: enter failsafe mode (stop the robot and all commands)
        pass

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

                    print(packet)
                except Exception:
                    print("Data transmission error!")
                    self._fail_safe_mode()
            else:
                self._fail_safe_mode()

    def _initialize_backend(self):
        if is_raspberry_pi():  # assuming ARM is Raspberry Pi
            self._gimbal_backend = SG90ServoGimbalBackend()
        else:
            self._gimbal_backend = DummyGimbalBackend()

    def __init__(self, host: str, port: int):
        self._initialize_backend()

        self._client_socket = None
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind((host, port))
        self._socket.listen(1)

        self._updater = Thread(target=self._handle_connection)
        self._updater.start()


parser = argparse.ArgumentParser(description='Connect to the robot and send control commands.')
parser.add_argument('host', metavar='host', type=str, help='server IP or hostname')
parser.add_argument('port', metavar='port', type=int, help='server port')
args = parser.parse_args()

server = RobotServer(args.host, args.port)
