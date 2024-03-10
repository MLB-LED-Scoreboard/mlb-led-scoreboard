import os

from driver import graphics

from screens import Screen
from screens.base import ScreenBase


class WeatherScreen(ScreenBase):

    MAX_DURATION_SECONDS = 3

    def __init__(self, *args):
        super(self.__class__, self).__init__(*args)

    def render(self):
        weather_text = "It's weathery"

        font = self.config.font("4x6")

        graphics.DrawText(self.canvas, font, 0, 10, (255, 255, 255), weather_text)

        if self.duration > self.MAX_DURATION_SECONDS * 1000:
            self.manager.request_next_screen(Screen.CLOCK)
