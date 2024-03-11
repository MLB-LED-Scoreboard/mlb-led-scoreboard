from driver import graphics

from screens.games.base import GameScreen


class PregameScreen(GameScreen):
    MAX_DURATION_SECONDS = 5

    def render(self):
        self.__render_start_time()

    def __render_start_time(self):
        time_text = str(self.game.datetime())
        coords = self.layout.coords("pregame.start_time")
        font, font_size = self.layout.font_for("pregame.start_time")
        # color = colors.graphics_color("pregame.start_time")
        # time_x = center_text_position(time_text, coords["x"], font["size"]["width"])

        color = (255, 255, 255)
        graphics.DrawText(self.canvas, font, 0, coords.y, color, time_text)
