try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from utils import get_font, get_file


class AtBatRenderer:
    """Renders the batter and pitcher."""

    def __init__(self, canvas, atbat, data):
        self.canvas = canvas
        self.batter = atbat.batter
        self.pitcher = atbat.pitcher
        self.data = data
        self.colors = data.config.scoreboard_colors
        self.default_colors = self.data.config.team_colors.color("default")
        self.bgcolor = self.colors.graphics_color("default.background")

    def render(self):

        self.batter_coords = self.data.config.layout.coords("atbat.batter")
        self.pitcher_coords = self.data.config.layout.coords("atbat.pitcher")

        self.__render_batter_text(self.batter, self.default_colors, self.batter_coords["x"], self.batter_coords["y"])
        self.__render_pitcher_text(
            self.pitcher, self.default_colors, self.pitcher_coords["x"], self.pitcher_coords["y"]
        )

    def __render_batter_text(self, batter, colors, x, y):
        text_color = self.default_colors["text"]
        text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
        font = self.data.config.layout.font("atbat.batter")
        batter_text = ("AB:" + batter)[:8]
        graphics.DrawText(self.canvas, font["font"], x, y, text_color_graphic, batter_text)

    def __render_pitcher_text(self, pitcher, colors, x, y):
        text_color = self.default_colors["text"]
        text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
        font = self.data.config.layout.font("atbat.pitcher")
        pitcher_text = ("P:" + pitcher)[:8]
        graphics.DrawText(self.canvas, font["font"], x, y, text_color_graphic, pitcher_text)
