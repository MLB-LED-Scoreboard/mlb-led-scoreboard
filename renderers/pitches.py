try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics


class PitchesRenderer:
    """Renders balls and strikes on the scoreboard."""

    def __init__(self, canvas, pitches, data):
        self.canvas = canvas
        self.pitches = pitches
        self.layout = data.config.layout
        self.colors = data.config.scoreboard_colors

    def render(self):
        font = self.layout.font("batter_count")
        coords = self.layout.coords("batter_count")
        pitches_color = self.colors.graphics_color("batter_count")
        batter_count_text = "{}-{}".format(self.pitches.balls, self.pitches.strikes)
        graphics.DrawText(self.canvas, font["font"], coords["x"], coords["y"], pitches_color, batter_count_text)
