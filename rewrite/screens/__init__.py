from enum import Enum

class Screen(Enum):
    CLOCK   = 1
    WEATHER = 2
    GAME    = 3

from screens.screen_manager import ScreenManager
