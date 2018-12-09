import argparse
import socketserver

from beerbot.server_packet import ControllerPacket


class RobotServer(socketserver.BaseRequestHandler):
    def _fail_safe_mode(self):
        # Todo: enter failsafe mode (stop the robot and all commands)
        pass

    def handle(self):
        while True:
            data_received = self.request.recv(ControllerPacket.size())
            if data_received:
                self.request.send(data_received)

                try:
                    packet = ControllerPacket(data_received)
                    print(packet)
                except Exception:
                    print("Data transmission error!")
                    self._fail_safe_mode()
            else:
                self._fail_safe_mode()


parser = argparse.ArgumentParser(description='Connect to the robot and send control commands.')
parser.add_argument('host', metavar='host', type=str, help='server IP or hostname')
parser.add_argument('port', metavar='port', type=int, help='server port')
args = parser.parse_args()

myServer = socketserver.TCPServer((args.host, args.port), RobotServer)
myServer.serve_forever()
