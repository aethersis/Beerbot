import time
import argparse
import socket
import sys

from beerbot.controller_backends.abstract_backend import AbstractControllerBackend
from beerbot.controller_backends.joystick_backend import JoystickBackend
from beerbot.server_packet import ControllerPacket

SEND_INTERVAL = 0.05  # send control signal every 50ms (20 fps)


def build_packet(controller_backend: AbstractControllerBackend) -> bytes:
    packet = ControllerPacket()
    packet.camera_yaw = controller_backend.left_yaw
    packet.camera_pitch = controller_backend.left_pitch
    packet.robot_yaw = controller_backend.right_yaw
    packet.robot_speed = controller_backend.right_pitch
    return packet.serialize()


parser = argparse.ArgumentParser(description='Connect to the robot and send control commands.')
parser.add_argument('host', metavar='host', type=str, help='server IP or hostname')
parser.add_argument('port', metavar='port', type=int, help='server port')
args = parser.parse_args()

joystick = JoystickBackend()

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((args.host, args.port))

while True:
    try:
        connection.send(build_packet(joystick))
        response_data = connection.recv(1024)
        time.sleep(0.05)
    except KeyboardInterrupt:
        connection.close()
        joystick.__del__()
        print("Good bye!")
        sys.exit()

