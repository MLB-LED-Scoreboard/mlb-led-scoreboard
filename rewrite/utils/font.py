import os

from dataclasses import dataclass

from driver import graphics


class FontCache:
    FONT_PATHS = ["../assets/fonts/patched", "../submodules/matrix/fonts"]

    def __init__(self, default_fontname):
        self.font_cache = {}
        self.default_fontname = default_fontname

        # Preload the default font
        self.default_font = self.fetch_font(self.default_fontname)

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

    def font_size(self, font_name):
        if font_name[-1] == "B":
            font_name = font_name[:-1]

        return tuple(int(part) for part in font_name.split("x"))
