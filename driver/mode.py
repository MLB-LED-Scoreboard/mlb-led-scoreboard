from enum import Enum


class DriverMode(Enum):
    HARDWARE           = 0  # Raspberry Pi 4 and earlier (hzeller)
    HARDWARE_PI5       = 1  # Raspberry Pi 5 (PioMatter)
    SOFTWARE_EMULATION = 2
