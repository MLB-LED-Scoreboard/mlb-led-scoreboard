import os, time

from driver import graphics

from screens import Screen
from screens.base import ScreenBase


class GameScreen(ScreenBase):
    MAX_DURATION_SECONDS = 3

    def render(self):
        weather_text = "It's a game!"

        font = self.config.font("4x6")

        graphics.DrawText(self.canvas, font, 0, 10, (255, 255, 255), weather_text)
