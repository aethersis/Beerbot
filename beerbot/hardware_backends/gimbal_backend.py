from abc import *

from beerbot.common.utilities import is_raspberry_pi, validate_value, remap


class AbstractGimbalBackend(ABC):
    @abstractproperty
    def yaw(self):
        pass

    @abstractproperty
    def pitch(self):
        pass


class DummyGimbalBackend(AbstractGimbalBackend):
    def __init__(self):
        self._yaw = 0.0
        self._pitch = 0.0

    @property
    def pitch(self):
        return self._yaw

    @property
    def yaw(self):
        return self._pitch

    @yaw.setter
    def yaw(self, value: float):
        validate_value(value, 'Camera yaw')
        self._yaw = value

    @pitch.setter
    def pitch(self, value: float):
        validate_value(value, 'Camera pitch')
        self._pitch = value


class SG90ServoGimbalBackend(AbstractGimbalBackend):
    def __init__(self, yaw_pin=6, pitch_pin=5):
        if not is_raspberry_pi():
            raise Exception("This class works only on Raspberry Pi")

        import pigpio
        self._yaw = 0.0
        self._pitch = 0.0
        self._angle_min = 1100
        self._angle_max = 2100
        self._yaw_pin = yaw_pin
        self._pitch_pin = pitch_pin
        self._pi = pigpio.pi('127.0.0.1', 8666)


    @property
    def pitch(self):
        return self._yaw

    @property
    def yaw(self):
        return self._pitch

    @yaw.setter
    def yaw(self, value: float):
        validate_value(value, 'Camera yaw')
        self._pi.set_servo_pulsewidth(self._yaw_pin, remap(-value, -1.0, 1.0, self._angle_min, self._angle_max))

    @pitch.setter
    def pitch(self, value: float):
        validate_value(value, 'Camera pitch')
        self._pi.set_servo_pulsewidth(self._pitch_pin, remap(-value, -1.0, 1.0, self._angle_min, self._angle_max))

