try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from renderers.scrollingtext import ScrollingText


class AtBatRenderer:
    """Renders the batter and pitcher."""

    def __init__(self, canvas, atbat, data, text_pos, strikeout, animation_time):
        self.canvas = canvas
        self.batter = atbat.batter
        self.pitcher = atbat.pitcher
        self.data = data
        self.colors = data.config.scoreboard_colors
        self.bgcolor = self.colors.graphics_color("default.background")
        self.strikeout = strikeout
        self.start_pos = text_pos
        self.animation_time = animation_time

    def render(self):
        plength = self.__render_pitcher_text()

        if self.strikeout and self.animation_time < 60:
            if (self.animation_time // 6) % 2:
                self.__render_strikeout()
            return plength
        else:
            blength = self.__render_batter_text()
            return max(plength, blength)

    def __render_strikeout(self):
        coords = self.data.config.layout.coords("atbat.strikeout")
        color = self.colors.graphics_color("atbat.strikeout")
        font = self.data.config.layout.font("atbat.strikeout")
        graphics.DrawText(self.canvas, font["font"], coords["x"], coords["y"], color, "K")

    def __render_batter_text(self):
        coords = self.data.config.layout.coords("atbat.batter")
        color = self.colors.graphics_color("atbat.batter")
        font = self.data.config.layout.font("atbat.batter")
        size = ScrollingText(
            self.canvas,
            coords["x"] + font["size"]["width"] * 3,
            coords["y"],
            coords["width"],
            font,
            color,
            self.bgcolor,
            self.batter,
        ).render(self.start_pos)
        graphics.DrawText(self.canvas, font["font"], coords["x"], coords["y"], color, "AB:")
        return size

    def __render_pitcher_text(self):
        coords = self.data.config.layout.coords("atbat.pitcher")
        color = self.colors.graphics_color("atbat.pitcher")
        font = self.data.config.layout.font("atbat.pitcher")

        size = ScrollingText(
            self.canvas,
            coords["x"] + font["size"]["width"] * 2,
            coords["y"],
            coords["width"],
            font,
            color,
            self.bgcolor,
            self.pitcher,
        ).render(self.start_pos)
        graphics.DrawText(self.canvas, font["font"], coords["x"], coords["y"], color, "P:")
        return size
