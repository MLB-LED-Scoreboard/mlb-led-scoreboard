from enum import Enum

mode = None

class DriverMode(Enum):
    HARDWARE           = 0
    SOFTWARE_EMULATION = 1


def is_hardware():
    return mode == DriverMode.HARDWARE

def is_emulated():
    return mode == DriverMode.SOFTWARE_EMULATION
