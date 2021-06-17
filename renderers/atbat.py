try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from renderers.scrollingtext import ScrollingText
from utils import get_font, get_file


class AtBatRenderer:
    """Renders the batter and pitcher."""

    def __init__(self, canvas, atbat, data, text_pos):
        self.canvas = canvas
        self.batter = atbat.batter
        self.pitcher = atbat.pitcher
        self.data = data
        self.colors = data.config.scoreboard_colors
        self.default_colors = self.data.config.team_colors.color("default")
        self.bgcolor = self.colors.graphics_color("default.background")

        self.start_pos = text_pos

    def render(self):

        batter_coords = self.data.config.layout.coords("atbat.batter")
        pitcher_coords = self.data.config.layout.coords("atbat.pitcher")

        blength = self.__render_batter_text(self.batter, batter_coords["x"], batter_coords["y"])
        plength = self.__render_pitcher_text(self.pitcher, pitcher_coords["x"], pitcher_coords["y"])

        return max(plength, blength)

    def __render_batter_text(self, batter, x, y):
        text_color = self.default_colors["text"]
        text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
        font = self.data.config.layout.font("atbat.batter")
        size = ScrollingText(
            self.canvas, x + font["size"]["width"] * 3, y, 20, font, text_color_graphic, self.bgcolor, batter
        ).render(self.start_pos)
        graphics.DrawText(self.canvas, font["font"], x, y, text_color_graphic, "AB:")
        return size

    def __render_pitcher_text(self, pitcher, x, y):
        text_color = self.default_colors["text"]
        text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
        font = self.data.config.layout.font("atbat.pitcher")

        size = ScrollingText(
            self.canvas, x + font["size"]["width"] * 2, y, 24, font, text_color_graphic, self.bgcolor, pitcher
        ).render(self.start_pos)
        graphics.DrawText(self.canvas, font["font"], x, y, text_color_graphic, "P:")
        return size
