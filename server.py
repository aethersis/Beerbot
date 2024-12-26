import argparse

from flask import Flask, send_from_directory
from flask_socketio import SocketIO

from backend.hardware_backends.chassis_backend import PCA9685CarChassis, DummyChassisBackend
from backend.hardware_backends.gimbal_backend import PCA9685GimbalBackend, DummyGimbalBackend
from backend.common.utilities import *
from backend.hardware_backends.pi_hats import PCA9685

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)


class RobotServer:
    def __init__(self):
        self._hat = None
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize hardware or dummy backends based on the environment."""
        if is_raspberry_pi():  # assuming ARM is Raspberry Pi
            print("Raspberry Pi detected. Using real hardware.")
            self._hat = PCA9685()
            self._gimbal_backend = PCA9685GimbalBackend(self._hat)
            self._chassis_backend = PCA9685CarChassis(self._hat)
        else:
            print("Unknown hardware platform. Running dummy hardware.")
            self._gimbal_backend = DummyGimbalBackend()
            self._chassis_backend = DummyChassisBackend()
        self._fail_safe_mode()

    def _fail_safe_mode(self):
        """Set all control inputs to safe defaults."""
        self._gimbal_backend.yaw = 0
        self._gimbal_backend.pitch = 0
        self._chassis_backend.yaw = 0
        self._chassis_backend.speed = 0

    def handle_control_packet(self, payload):
        """Handle incoming control data."""
        try:
            self._gimbal_backend.yaw = payload[0]
            self._gimbal_backend.pitch = payload[1]
            self._chassis_backend.yaw = payload[2]
            self._chassis_backend.speed = payload[3]
        except Exception as e:
            print(f"Error handling control packet: {e}")
            self._fail_safe_mode()


# Initialize the RobotServer
robot = RobotServer()

# Flask Routes
@app.route('/')
def serve_index():
    """Serve the main HTML file."""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files like JS, CSS, and images."""
    return send_from_directory('frontend', path)

# WebSocket Event Handlers
@socketio.on('control')
def handle_control(data):
    print(f"Received control data: {data}")
    robot.handle_control_packet(data)

@socketio.on('connect')
def handle_connect():
    print("WebSocket client connected.")

@socketio.on('disconnect')
def handle_disconnect():
    print("WebSocket client disconnected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Connect to the robot and send control commands.')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host IP to bind the server to.')
    parser.add_argument('--port', type=int, default=9000, help='Port to bind the server to.')
    args = parser.parse_args()

    print(f"Starting server on {args.host}:{args.port}")
    socketio.run(app, host=args.host, port=args.port, allow_unsafe_werkzeug=True)