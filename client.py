import time
import argparse
import socket
import sys

from beerbot.hardware_backends.joystick_backend import *
from beerbot.common.server_packet import ControllerPacket

SEND_INTERVAL = 0.05  # send control signal every 50ms (20 fps)


def build_packet(controller_backend: AbstractControllerBackend) -> bytes:
    packet = ControllerPacket()
    packet.camera_yaw = controller_backend.left_yaw
    packet.camera_pitch = controller_backend.left_pitch
    packet.robot_yaw = controller_backend.right_yaw
    packet.robot_speed = controller_backend.right_pitch
    print(packet)
    return packet.serialize()


parser = argparse.ArgumentParser(description='Connect to the robot and send control commands.')
parser.add_argument('host', metavar='host', type=str, help='server IP or hostname')
parser.add_argument('port', metavar='port', type=int, help='server port')
args = parser.parse_args()

joystick = GenesysP65Backend()

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connection.connect((args.host, args.port))

while True:
    try:
        packet = build_packet(joystick)
        connection.send(packet)
        response_data = connection.recv(ControllerPacket.size())

        if response_data != packet:
            print("Invalid server reply!")

        time.sleep(SEND_INTERVAL)
    except KeyboardInterrupt:
        connection.close()
        joystick.__del__()
        print("Good bye!")
        sys.exit()

