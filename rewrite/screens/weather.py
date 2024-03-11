import os

from driver import graphics

from screens import Screen
from screens.base import ScreenBase


class WeatherScreen(ScreenBase):
    MAX_DURATION_SECONDS = 3

    def render(self):
        weather_text = "It's weathery"

        font, font_size = self.config.layout.font("4x6")

        graphics.DrawText(self.canvas, font, 0, 10, (255, 255, 255), weather_text)

        if self.duration > WeatherScreen.MAX_DURATION_SECONDS * 1000:
            self.manager.request_next_screen(Screen.CLOCK)
