import os

from driver import graphics

class FontCache:

    FONT_PATHS = ["../assets/fonts/patched", "../submodules/matrix/fonts"]

    def __init__(self):
        self.font_cache = {}

    def fetch_font(self, font_name):
        if font_name in self.font_cache:
            return self.font_cache[font_name]

        for font_path in self.FONT_PATHS:
            path = f"{font_path}/{font_name}.bdf"
            if os.path.isfile(path):
                font = graphics.Font()
                font.LoadFont(path)

                self.font_cache[font_name] = font

        return font
