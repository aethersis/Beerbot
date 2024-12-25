from abc import ABC, abstractproperty

from backend.common.utilities import validate_value, is_raspberry_pi, clamp, remap


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


class PCA9685CarChassis(AbstractChassisBackend):
    """
    Car chassis that uses a PWM controller PCA9685 available as a WaveShare Servo Driver HAT.
    This is the best option to drive off the shelf RC cars.
    Turning is achieved by controlling a servo that turns forward wheels.
    Forward and backward movement is achieved by sending a PWM signal to an ESC (brushed or brushless).
    """
    from backend.hardware_backends.pi_hats import PCA9685

    def __init__(self, pca9685hat: PCA9685, max_speed=0.25, yaw_channel=1, speed_channel=0):
        """
        :param pca9685hat: instance of PCA9685 class to communicate with the Waveshare servo driver hat
        :param max_speed: maximum allowed speed from 0 to 1
        :param yaw_channel: servo channel for steering control
        :param speed_channel: servo channel for speed control (i.e. connected to brushless ESC)
        """
        if not is_raspberry_pi():
            raise Exception("This class works only on Raspberry Pi")

        self._yaw = 0.0
        self._speed = 0.0
        self._max_speed = 0.1

        self._hat = pca9685hat
        self._yaw_channel = yaw_channel
        self._speed_channel = speed_channel

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
        self._hat.set_servo_pulse(self._yaw_channel, remap(value, -1.0, 1.0, 500, 2500))

    @speed.setter
    def speed(self, value):
        validate_value(value, 'Platform speed')
        self._speed = value * self._max_speed
        self._hat.set_servo_pulse(self._speed_channel, remap(value, -1.0, 1.0, 500, 2500))


class L298TankChassis(AbstractChassisBackend):
    """
    Tank chassis that uses PWM control directly from GPIO pins (see __init__)
    to control a dual channel H-bridge DC motor controller such as L298-N
    The tank has one motor per track, so controlling "yaw" is achieved by
    varying the speed of each track individually to achieve turning or
    forward movement.
    """
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