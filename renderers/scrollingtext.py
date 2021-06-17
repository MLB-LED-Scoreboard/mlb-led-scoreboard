try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from utils import center_text_position


class ScrollingText:
    def __init__(self, canvas, x, y, width, font, text_color, background_color, text):
        self.canvas = canvas
        self.text = text
        self.text_color = text_color
        self.bg_color = background_color
        self.font = font
        self.x = x
        self.y = y
        self.width = width

    def render(self, scroll_pos):
        if self.__text_should_scroll():
            x = scroll_pos
            pos = graphics.DrawText(self.canvas, self.font["font"], x, self.y, self.text_color, self.text)
            h = self.font["size"]["height"]
            for x in range(self.x):
                graphics.DrawLine(self.canvas, x, self.y, x, self.y - h, self.bg_color)
            for x in range(self.x + self.width, self.canvas.width):
                graphics.DrawLine(self.canvas, x, self.y, x, self.y - h, self.bg_color)
            return pos

        else:
            graphics.DrawText(
                self.canvas, self.font["font"], self.__center_position(), self.y, self.text_color, self.text
            )
            return 0

    # Maybe the text is too short and we should just center it instead?
    def __text_should_scroll(self):
        return len(self.text) * self.font["size"]["width"] > self.width

    def __center_position(self):
        return center_text_position(self.text, abs(self.width // 2) + self.x, self.font["size"]["width"])
