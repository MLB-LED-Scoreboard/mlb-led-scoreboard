import Bullpen
from driver import graphics

class MLBLEDScoreboardScreen(Bullpen.Action):

    SCROLLABLE = False
    DEFAULT_REFRESH_RATE = 0.05 # seconds

    def __init__(self, matrix, canvas, data):
        self.matrix = matrix
        self.canvas = canvas
        self.data = data
        self.scroll_position = self.canvas.width

        self.on_perform = self._on_render

    def on_render(self):
        raise NotImplementedError
    
    def _on_render(self):
        self.canvas.Fill(
            self.background_color.red,
            self.background_color.green,
            self.background_color.blue
        )

        self.on_render()

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def ready_to_rotate(self):
        if self.SCROLLABLE and self.data.config.rotation_scroll_until_finished:
            return self.data.scrolling_finished
        
        return True

    def update_scroll_position(self, text_length, end):
        after_scroll = self.scroll_position - 1

        if after_scroll + text_length < 0:
            self.data.scrolling_finished = True

            if after_scroll + text_length < -10:
                self.scroll_position = end
                return

        self.scroll_position = after_scroll

    @property
    def background_color(self):
        return self.data.config.scoreboard_colors.graphics_color("default.background")
