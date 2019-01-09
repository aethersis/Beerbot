import pickle
from beerbot.common.utilities import validate_value


class ControllerPacket:
    def __init__(self, raw_data: bytes = None):
        #  this value is guaranteed to be smaller than int on pretty much any reasonable architecture
        #  at the same time, the precission is sufficiently high to keep everything smooth and keep packet small
        self._resolution = 65535

        if raw_data is not None:
            self.deserialize(raw_data)
        else:
            self._camera_yaw = 0.0
            self._camera_pitch = 0.0
            self._robot_yaw = 0.0
            self._robot_speed = 0.0

    def _from_int(self, value: int) -> float:
        return value / float(self._resolution)

    def _to_int(self, value: float) -> int:
        return int(value * self._resolution)

    @property
    def camera_yaw(self):
        return self._camera_yaw

    @camera_yaw.setter
    def camera_yaw(self, value: float):
        validate_value(value, 'Camera yaw')
        self._camera_yaw = value
        
    @property
    def camera_pitch(self):
        return self._camera_pitch

    @camera_pitch.setter
    def camera_pitch(self, value: float):
        validate_value(value, 'Camera pitch')
        self._camera_pitch = value
        
    @property
    def robot_yaw(self):
        return self._robot_yaw

    @robot_yaw.setter
    def robot_yaw(self, value: float):
        validate_value(value, 'Robot yaw')
        self._robot_yaw = value
    
    @property
    def robot_speed(self):
        return self._robot_speed

    @robot_speed.setter
    def robot_speed(self, value: float):
        validate_value(value, 'Robot speed')
        self._robot_speed = value

    def serialize(self) -> bytes:
        raw_data = (self._to_int(self.camera_yaw),
                    self._to_int(self._camera_pitch),
                    self._to_int(self._robot_yaw),
                    self._to_int(self._robot_speed))

        return pickle.dumps(raw_data)

    def deserialize(self, raw_data: bytes):
        raw_data = pickle.loads(raw_data)
        self.camera_yaw = self._from_int(raw_data[0])
        self.camera_pitch = self._from_int(raw_data[1])
        self.robot_yaw = self._from_int(raw_data[2])
        self._robot_speed = self._from_int(raw_data[3])

    @staticmethod
    def size():
        # A proper way is needed to determine what can be the maximum size of the packet while using pickle.
        # The following value is a bit bigger than necessary to stay safe
        return 32

    def __str__(self):
        return "Camera yaw: {}\n" \
               "Camera pitch: {}\n" \
               "Robot yaw: {}\n" \
               "Robot speed: {}\n".\
                format(self.camera_yaw,
                       self.camera_pitch,
                       self.robot_yaw,
                       self.robot_speed)
