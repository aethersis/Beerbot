from abc import ABC, abstractproperty

from beerbot.common.utilities import validate_value, is_raspberry_pi, clamp


class AbstractChassisBackend(ABC):
    @abstractproperty
    def yaw(self):
        pass

    @abstractproperty
    def speed(self):
        pass


class DummyChassisBackend(AbstractChassisBackend):
    def __init__(self):
        self._yaw = 0.0
        self._speed = 0.0

    @property
    def speed(self):
        return self._speed

    @property
    def yaw(self):
        return self._yaw

    @yaw.setter
    def yaw(self, value: float):
        validate_value(value, 'Camera yaw')
        self._yaw = value

    @speed.setter
    def speed(self, value: float):
        validate_value(value, 'Camera pitch')
        self._speed = value


class HBridgeMotorizedChassis(AbstractChassisBackend):
    def __init__(self):
        if not is_raspberry_pi():
            raise Exception("This class works only on Raspberry Pi")

        from gpiozero import PWMOutputDevice, OutputDevice
        self._yaw = 0.0
        self._speed = 0.0

        self._pwm_left = PWMOutputDevice(18, frequency=440)
        self._forward_left = OutputDevice(4)
        self._backward_left = OutputDevice(3)

        self._forward_right = OutputDevice(17)
        self._backward_right = OutputDevice(27)
        self._pwm_right = PWMOutputDevice(22, frequency=440)

    def _set_speeds(self):
        dead_zone = 0.1
        left_track = clamp(self._speed - self._yaw)
        right_track = clamp(self._speed + self._yaw)
        print(left_track, right_track)
        self._pwm_left.value = abs(left_track)
        self._pwm_right.value = abs(right_track)

        if left_track > dead_zone:
            self._forward_left.on()
            self._backward_left.off()
        elif left_track < -dead_zone:
            self._forward_left.off()
            self._backward_left.on()
        else:
            self._forward_left.off()
            self._backward_left.off()

        if right_track > dead_zone:
            self._forward_right.on()
            self._backward_right.off()
        elif right_track < -dead_zone:
            self._forward_right.off()
            self._backward_right.on()
        else:
            self._forward_right.off()
            self._backward_right.off()
            
    @property
    def yaw(self):
        return self._yaw

    @property
    def speed(self):
        return self._speed

    @yaw.setter
    def yaw(self, value):
        validate_value(value, 'Platform yaw')
        self._yaw = value
        self._set_speeds()

    @speed.setter
    def speed(self, value):
        validate_value(value, 'Platform speed')
        self._speed = value
        self._set_speeds()
