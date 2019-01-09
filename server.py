import argparse
import socket
from threading import Thread

from beerbot.hardware_backends.chassis_backend import HBridgeMotorizedChassis, DummyChassisBackend
from beerbot.hardware_backends.gimbal_backend import SG90ServoGimbalBackend, DummyGimbalBackend
from beerbot.common.server_packet import ControllerPacket
from beerbot.common.utilities import *


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
                    self._chassis_backend.yaw = packet.robot_yaw
                    self._chassis_backend.speed = packet.robot_speed
                except Exception as e:
                    print("Data transmission error: " + e.__str__())
                    self._fail_safe_mode()
            else:
                self._fail_safe_mode()

    def _clear_screen(self):
        os.system(self._clear_screen_command)

    def _initialize_backend(self):
        if is_raspberry_pi():  # assuming ARM is Raspberry Pi
            self._clear_screen_command = 'clear'
            self._gimbal_backend = SG90ServoGimbalBackend()
            self._chassis_backend = HBridgeMotorizedChassis()
        else:
            self._clear_screen_command = 'cls'
            self._gimbal_backend = DummyGimbalBackend()
            self._chassis_backend = DummyChassisBackend()

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
