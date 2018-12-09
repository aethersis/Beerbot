from abc import *

from utilities import is_raspberry_pi, validate_value


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
    def __init__(self, yaw_pin=18, pitch_pin=19):
        if not is_raspberry_pi():
            raise Exception("This class works only on Raspberry Pi")

        import wiringpi
        self._yaw = 0.0
        self._pitch = 0.0
        self._yaw_pin = yaw_pin
        self._pitch_pin = pitch_pin

        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(yaw_pin, wiringpi.GPIO.OUTPUT)
        wiringpi.pinMode(pitch_pin, wiringpi.GPIO.OUTPUT)
        wiringpi.softPwmCreate(yaw_pin, 50, 100)
        wiringpi.softPwmCreate(pitch_pin, 50, 100)

    def _valueToPwm(self, value: float) -> int:
        return int(100 * (value + 1.0)/2.0)

    @property
    def pitch(self):
        return self._yaw

    @property
    def yaw(self):
        return self._pitch

    @yaw.setter
    def yaw(self, value: float):
        import wiringpi
        validate_value(value, 'Camera yaw')
        self._yaw = value
        wiringpi.pwmWrite(self._yaw_pin, self._valueToPwm(value))

    @pitch.setter
    def pitch(self, value: float):
        import wiringpi
        validate_value(value, 'Camera pitch')
        self._pitch = value
        wiringpi.pwmWrite(self._pitch_pin, self._valueToPwm(value))