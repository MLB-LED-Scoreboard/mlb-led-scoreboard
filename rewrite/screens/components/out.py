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
            

    # TODO: The size coordinates for these boxes are off-by-one because they fail to account for endpoints.
    #       i.e. `size` config of 2 renders a 3x3 box instead of 2x2 because endpoints for graphics.DrawLine are inclusive.
    def __render_outline(self, coords, color):
        x, y, size = coords.x, coords.y, coords.size

        DrawRect(self.canvas, x, y, size + 1, size + 1, color, filled=False)

    def __render_out(self, coords, color):
        x, y, size = coords.x, coords.y, coords.size

        DrawRect(self.canvas, x, y, size + 1, size + 1, color, filled=True)

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