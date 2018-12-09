from abc import *

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
