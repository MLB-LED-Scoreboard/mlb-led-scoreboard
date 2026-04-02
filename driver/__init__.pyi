'''
Signatures for driver module.
The driver proxies attribute access to HW or SW packages depending on emulation state.
'''

from RGBMatrixEmulator import graphics as graphics
from RGBMatrixEmulator import RGBMatrix as RGBMatrix
from RGBMatrixEmulator import RGBMatrixOptions as RGBMatrixOptions

__version__: str
hardware_load_failed: bool

def is_hardware() -> bool: ...
def is_emulated() -> bool: ...
