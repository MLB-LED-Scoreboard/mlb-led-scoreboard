import Bullpen
from driver import graphics

class MLBLEDScoreboardScreen(Bullpen.Action):

    def __init__(self, matrix, canvas, data):
        self.matrix = matrix
        self.canvas = canvas
        self.data = data
        self.scroll_position = self.canvas.width

        self.on_perform = self.on_render

    def on_render(self):
        raise NotImplementedError
    
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
        return self.data.config.scoreboard_colors.color("default.background")
