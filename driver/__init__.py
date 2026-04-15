import sys

from utils import args
from driver.mode import DriverMode

class DriverWrapper:
    def __init__(self):
        self.hardware_load_failed = False
        self.mode = None

        if 'unittest' in sys.modules or args().emulated:
            self.set_mode(DriverMode.SOFTWARE_EMULATION)
        elif args().pi5:
            # User explicitly requested Pi 5 mode
            self.set_mode(DriverMode.HARDWARE_PI5)
        else:
            # Default to Pi 4 / hzeller mode
            self.set_mode(DriverMode.HARDWARE)


    @property
    def __name__(self):
        return 'driver'

    def is_hardware(self):
        return self.mode == DriverMode.HARDWARE or self.mode == DriverMode.HARDWARE_PI5

    def is_emulated(self):
        return self.mode == DriverMode.SOFTWARE_EMULATION
    
    def is_pi5(self):
        return self.mode == DriverMode.HARDWARE_PI5

    def set_mode(self, mode):
        self.mode = mode

        if self.mode == DriverMode.HARDWARE_PI5:
            # Raspberry Pi 5 mode using PioMatter
            try:
                from driver.piomatter_adapter import (
                    PioMatterMatrixAdapter,
                    PioMatterGraphicsAdapter
                )
                
                # Store the adapter classes
                self._matrix_adapter = PioMatterMatrixAdapter
                self._graphics_adapter = PioMatterGraphicsAdapter()
                
            except ImportError as e:
                print(f"Failed to import PioMatter library: {e}")
                print("Falling back to software emulation.")
                import RGBMatrixEmulator
                self.mode = DriverMode.SOFTWARE_EMULATION
                self.driver = RGBMatrixEmulator
                self.hardware_load_failed = True
                
        elif self.mode == DriverMode.HARDWARE:
            # Raspberry Pi 4 and earlier using hzeller rgbmatrix
            try:
                from driver.hzeller_adapter import (
                    HzellerMatrixAdapter,
                    HzellerGraphicsAdapter
                )
                
                # Store the adapter classes
                self._matrix_adapter = HzellerMatrixAdapter
                self._graphics_adapter = HzellerGraphicsAdapter()
                
            except ImportError:
                # Fall back to RGBMatrixEmulator if rgbmatrix not available
                import RGBMatrixEmulator
                self.mode = DriverMode.SOFTWARE_EMULATION
                self.driver = RGBMatrixEmulator
                self.hardware_load_failed = True
        else:
            # Software emulation mode
            import RGBMatrixEmulator
            self.driver = RGBMatrixEmulator

    def RGBMatrix(self, options):
        """Create an RGBMatrix instance using the appropriate adapter."""
        if self.mode == DriverMode.HARDWARE_PI5 or self.mode == DriverMode.HARDWARE:
            return self._matrix_adapter(options)
        else:
            # Emulator mode
            return self.driver.RGBMatrix(options=options)
    
    @property
    def graphics(self):
        """Return the graphics adapter."""
        if self.mode == DriverMode.HARDWARE_PI5 or self.mode == DriverMode.HARDWARE:
            return self._graphics_adapter
        else:
            return self.driver.graphics

    def __getattr__(self, name):
        """
        Proxy attribute access to the underlying driver.
        For adapters, we need to handle special cases.
        """
        if self.mode == DriverMode.HARDWARE_PI5 or self.mode == DriverMode.HARDWARE:
            # For adapter modes, check if it's a known attribute
            if name == 'RGBMatrixOptions':
                if self.mode == DriverMode.HARDWARE:
                    import rgbmatrix
                    return rgbmatrix.RGBMatrixOptions
                else:
                    # Pi 5 mode - create a simple options class
                    return _create_pi5_options_class()
            elif name == '__version__':
                return 'adapter-1.0.0'
            elif name == 'graphics':
                return self._graphics_adapter
        
        # Default: pass through to driver
        if 'driver' in self.__dict__:
            return getattr(self.driver, name)
        
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


def _create_pi5_options_class():
    """Create a simple options class compatible with Pi 5."""
    class RGBMatrixOptions:
        def __init__(self):
            self.rows = 32
            self.cols = 64
            self.chain_length = 1
            self.parallel = 1
            self.hardware_mapping = 'active3-bgr'  # Default for Seekgreat boards (BGR color order)
            self.gpio_slowdown = 4
            self.brightness = 100
            self.pwm_bits = 11
            self.pwm_lsb_nanoseconds = 130
            self.led_rgb_sequence = "RGB"
            self.pixel_mapper_config = ""
            self.panel_type = ""
            self.multiplexing = 0
            
    return RGBMatrixOptions


sys.modules['driver'] = DriverWrapper()
