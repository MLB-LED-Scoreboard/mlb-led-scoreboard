try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics


class OutsRenderer:
    """Renders the out circles on the scoreboard."""

    def __init__(self, canvas, outs, data):
        self.canvas = canvas
        self.outs = outs
        self.layout = data.config.layout
        self.colors = data.config.scoreboard_colors

    def render(self):
        out_px = []
        out_px.append(self.layout.coords("outs.1"))
        out_px.append(self.layout.coords("outs.2"))
        out_px.append(self.layout.coords("outs.3"))

        colors = []
        colors.append(self.colors.graphics_color("outs.1"))
        colors.append(self.colors.graphics_color("outs.2"))
        colors.append(self.colors.graphics_color("outs.3"))

        for out in range(len(out_px)):
            self.__render_out_circle(out_px[out], colors[out])
            # Fill in the circle if that out has occurred
            if self.outs.number > out:
                self.__fill_circle(out_px[out], colors[out])

    def __render_out_circle(self, out, color):
        x, y, size = (out["x"], out["y"], out["size"])
        graphics.DrawLine(self.canvas, x, y, x + size, y, color)
        graphics.DrawLine(self.canvas, x, y, x, y + size, color)
        graphics.DrawLine(self.canvas, x + size, y + size, x, y + size, color)
        graphics.DrawLine(self.canvas, x + size, y + size, x + size, y, color)

    def __fill_circle(self, out, color):
        size = out["size"]
        x, y = (out["x"], out["y"])
        for y_offset in range(size):
            graphics.DrawLine(self.canvas, x, y + y_offset, x + size, y + y_offset, color)
