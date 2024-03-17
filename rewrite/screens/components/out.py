from driver import graphics

from utils.graphics import DrawRect

class Out:
    def __init__(self, number, screen):
        self.number = number
        self.screen = screen

    def render(self):
        color = self.colors.graphics_color(f"outs.{self.number}")
        coords = self.layout.coords(f"outs.{self.number}")

        if self.game.outs() >= self.number:
            self.__render_out(coords, color)
        else:
            self.__render_outline(coords, color)
            

    def __render_outline(self, coords, color):
        x, y, size = coords.x, coords.y, coords.size

        DrawRect(self.canvas, x, y, size, size, color, filled=False)

    def __render_out(self, coords, color):
        x, y, size = coords.x, coords.y, coords.size

        DrawRect(self.canvas, x, y, size, size, color, filled=True)

    @property
    def game(self):
        return self.screen.game

    @property
    def canvas(self):
        return self.screen.canvas

    @property
    def config(self):
        return self.screen.config

    @property
    def colors(self):
        return self.screen.colors

    @property
    def layout(self):
        return self.screen.layout