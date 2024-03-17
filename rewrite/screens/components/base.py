from driver import graphics

class Base:
    def __init__(self, number, screen):
        self.number = number
        self.screen = screen

    def render(self):
        color = self.colors.graphics_color(f"bases.{self.number}B")
        coords = self.layout.coords(f"bases.{self.number}B")

        self.__render_outline(coords, color)

        if self.game.man_on(self.number):
            self.__render_runner(coords, color)

    def __render_outline(self, coords, color):
        x, y = coords.x, coords.y
        size = coords.size
        half = abs(size // 2)

        graphics.DrawLine(self.canvas, x + half, y, x, y + half, color)
        graphics.DrawLine(self.canvas, x + half, y, x + size, y + half, color)
        graphics.DrawLine(self.canvas, x + half, y + size, x, y + half, color)
        graphics.DrawLine(self.canvas, x + half, y + size, x + size, y + half, color)

    def __render_runner(self, coords, color):       
        x, y = coords.x, coords.y
        size = coords.size
        half = abs(size // 2)
        for offset in range(1, half + 1):
            graphics.DrawLine(self.canvas, x + half - offset, y + size - offset, x + half + offset, y + size - offset, color)
            graphics.DrawLine(self.canvas, x + half - offset, y + offset, x + half + offset, y + offset, color)

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