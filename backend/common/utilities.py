import platform

def clamp(value, range_from=-1.0, range_to=1.0):
    return max(min(value, range_to), range_from)


def validate_value(value: float, name: str, range_from=-1.0, range_to=1.0):
    if not range_from <= value <= range_to:
        raise ValueError("{} must be in range from {} to {}".format(name, range_from, range_to))


def is_raspberry_pi() -> bool:
    return ("arm" or "rpi") in platform.platform()


def remap(value, old_min, old_max, new_min, new_max):
    old_range = (old_max - old_min)
    new_range = (new_max - new_min)
    return (((value - old_min) * new_range) / old_range) + new_min
