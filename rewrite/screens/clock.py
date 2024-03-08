import os, time

from driver import graphics

from screens import Screen
from screens.base import ScreenBase


class ClockScreen(ScreenBase):

    MAX_DURATION_SECONDS = 3

    def __init__(self, *args):
        ScreenBase.__init__(self, *args)

    def render(self):
        time_format_str = "%H:%M%p"
        time_text = time.strftime(time_format_str)

        font_paths = ["../assets/fonts/patched", "../submodules/matrix/fonts"]
        for font_path in font_paths:
            path = f"{font_path}/4x6.bdf"
            if os.path.isfile(path):
                font = graphics.Font()
                font.LoadFont(path)

        graphics.DrawText(self.canvas, font, 5, 5, (255, 255, 255), time_text)

        if self.duration > self.MAX_DURATION_SECONDS * 1000:
            self.request_next_screen(Screen.WEATHER)
