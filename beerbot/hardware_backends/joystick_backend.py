from threading import Thread
from abc import *
import pygame

from beerbot.utilities import clamp


class AbstractControllerBackend(ABC):
    @abstractproperty
    def left_yaw(self):
        return 0

    @abstractproperty
    def left_pitch(self):
        return 0

    @abstractproperty
    def right_yaw(self):
        return 0

    @abstractproperty
    def right_pitch(self):
        return 0


class GenesysP65Backend(AbstractControllerBackend):
    def __init__(self, joystick_id=0, left_yaw_axis_id=0,
                 left_pitch_axis_id=1, right_yaw_axis_id=4, right_pitch_axis_id=3):
        self._axis_0_yaw = left_yaw_axis_id
        self._axis_0_pitch = left_pitch_axis_id
        self._axis_1_yaw = right_yaw_axis_id
        self._axis_1_pitch = right_pitch_axis_id

        self._left_yaw = 0.0
        self._left_pitch = 0.0
        self._right_yaw = 0.0
        self._right_pitch = 0.0

        pygame.init()
        pygame.joystick.init()
        self._joystick = pygame.joystick.Joystick(joystick_id)
        self._joystick.init()

        self._finished = False
        self._updater = Thread(target=self._read_joystick)
        self._updater.start()

    def __del__(self):
        self._finished = True

    def _read_joystick(self):
        while not self._finished:
            event = pygame.event.wait()
            if event.type == pygame.JOYAXISMOTION:
                e = event.dict
                value = clamp(e['value'])
                if e['axis'] == self._axis_0_yaw:
                    self._left_yaw = value
                elif e['axis'] == self._axis_1_yaw:
                    self._right_yaw = value
                elif e['axis'] == self._axis_0_pitch:
                    self._left_pitch = value * -1.0
                elif e['axis'] == self._axis_1_pitch:
                    self._right_pitch = value * -1.0

    @property
    def left_pitch(self):
        return self._left_pitch

    @property
    def left_yaw(self):
        return self._left_yaw

    @property
    def right_yaw(self):
        return self._right_yaw

    @property
    def right_pitch(self):
        return self._right_pitch
