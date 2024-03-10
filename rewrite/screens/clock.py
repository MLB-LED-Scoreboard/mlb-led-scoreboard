import os, time

from driver import graphics

from screens import Screen
from screens.base import ScreenBase


class ClockScreen(ScreenBase):
    MAX_DURATION_SECONDS = 3

    def render(self):
        time_format_str = "%H:%M%p"
        time_text = time.strftime(time_format_str)

        font = self.config.font("4x6")

        graphics.DrawText(self.canvas, font, 5, 5, (255, 255, 255), time_text)

        if self.duration > self.MAX_DURATION_SECONDS * 1000:
            self.manager.request_next_screen(Screen.WEATHER)
