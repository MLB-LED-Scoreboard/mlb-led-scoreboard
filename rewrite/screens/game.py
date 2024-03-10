import os, time

from driver import graphics

from screens import Screen
from screens.base import ScreenBase


class GameScreen(ScreenBase):

    MAX_DURATION_SECONDS = 3

    def __init__(self, manager, data):
        super(self.__class__, self).__init__(manager)

        self.data = data

    def render(self):
        weather_text = "It's a game!"

        font_paths = ["../assets/fonts/patched", "../submodules/matrix/fonts"]
        for font_path in font_paths:
            path = f"{font_path}/4x6.bdf"
            if os.path.isfile(path):
                font = graphics.Font()
                font.LoadFont(path)

        graphics.DrawText(self.canvas, font, 0, 10, (255, 255, 255), weather_text)
