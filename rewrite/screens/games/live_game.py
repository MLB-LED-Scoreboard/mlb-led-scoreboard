from driver import graphics

from screens.games.base import GameScreen


class LiveGameScreen(GameScreen):
    MAX_DURATION_SECONDS = 5

    def render(self):
        game_text = "It's a game!"

        font, font_size = self.config.layout.font("4x6")

        graphics.DrawText(self.canvas, font, 0, 10, (255, 255, 255), game_text)
