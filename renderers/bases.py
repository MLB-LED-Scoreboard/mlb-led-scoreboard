try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

import data.layout
from data.layout import Layout


class BasesRenderer:
    """Renders the bases on the scoreboard and fills them in if they
    currently hold a runner."""

    def __init__(self, canvas, bases, data):
        self.canvas = canvas
        self.bases = bases
        self.layout = data.config.layout
        self.colors = data.config.scoreboard_colors

    def render(self):
        base_runners = self.bases.runners
        colors = []
        colors.append(self.colors.graphics_color("bases.1B"))
        colors.append(self.colors.graphics_color("bases.2B"))
        colors.append(self.colors.graphics_color("bases.3B"))

        base_px = []
        base_px.append(self.layout.coords("bases.1B"))
        base_px.append(self.layout.coords("bases.2B"))
        base_px.append(self.layout.coords("bases.3B"))

        for base in range(len(base_runners)):
            self.__render_base_outline(base_px[base], colors[base])

            # Fill in the base if there's currently a baserunner
            if base_runners[base]:
                self.__render_baserunner(base_px[base], colors[base])

    def __render_base_outline(self, base, color):
        x, y = (base["x"], base["y"])
        size = base["size"]
        half = abs(size // 2)
        graphics.DrawLine(self.canvas, x + half, y, x, y + half, color)
        graphics.DrawLine(self.canvas, x + half, y, x + size, y + half, color)
        graphics.DrawLine(self.canvas, x + half, y + size, x, y + half, color)
        graphics.DrawLine(self.canvas, x + half, y + size, x + size, y + half, color)

    def __render_baserunner(self, base, color):
        x, y = (base["x"], base["y"])
        size = base["size"]
        half = abs(size // 2)
        for offset in range(1, half + 1):
            graphics.DrawLine(
                self.canvas, x + half - offset, y + size - offset, x + half + offset, y + size - offset, color
            )
            graphics.DrawLine(self.canvas, x + half - offset, y + offset, x + half + offset, y + offset, color)
