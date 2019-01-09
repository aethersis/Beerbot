import os

def clamp(value, range_from=-1.0, range_to=1.0):
    return max(min(value, range_to), range_from)


def validate_value(value: float, name: str, range_from=-1.0, range_to=1.0):
    if not range_from <= value <= range_to:
        raise ValueError("{} must be in range from {} to {}".format(name, range_from, range_to))


def is_raspberry_pi() -> bool:
    return os.uname()[4][:3] == 'arm'