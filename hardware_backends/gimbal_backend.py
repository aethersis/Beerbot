from abc import *

from common.utilities import is_raspberry_pi, validate_value


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
        self._validate_value(value, 'Camera yaw')
        self._yaw = value

    @pitch.setter
    def pitch(self, value: float):
        self._validate_value(value, 'Camera pitch')
        self._pitch = value


class SG90ServoGimbalBackend(AbstractGimbalBackend):
    def __init__(self, yaw_pin=20, pitch_pin=21):
        if not is_raspberry_pi():
            raise Exception("This class works only on Raspberry Pi")

        from gpiozero import AngularServo
        self._yaw = 0.0
        self._pitch = 0.0
        self._angle_min = -90
        self._angle_max = 90
        
        self._yaw_servo = AngularServo(yaw_pin, min_angle=self._angle_min, max_angle=self._angle_max)
        self._pitch_servo = AngularServo(pitch_pin, min_angle=self._angle_min, max_angle=self._angle_max)

    def _valueToAngle(self, value: float) -> int:
        return int((((value - (-1.0)) * (self._angle_max - self._angle_min)) / 2.0) + self._angle_max)

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
        self._yaw_servo.angle = self._valueToAngle(value)

    @pitch.setter
    def pitch(self, value: float):
        validate_value(value, 'Camera pitch')
        self._pitch = value
        self._pitch_servo.angle = self._valueToAngle(value)
