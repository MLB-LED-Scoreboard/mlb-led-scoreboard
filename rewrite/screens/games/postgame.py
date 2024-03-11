import os, time

from driver import graphics

from screens.games.base import GameScreen


class PostGameScreen(GameScreen):
    MAX_DURATION_SECONDS = 5

    def render(self):
        game_text = "It's a post-game!"

        font, font_size = self.config.layout.font("4x6")

        graphics.DrawText(self.canvas, font, 0, 10, (255, 255, 255), game_text)

    def _render_decision_scroll(self):
        coords = self.manager.layout.coords("final.scrolling_text")
        font, font_size = self.manager.layout.font("final.scrolling_text")

        # color = colors.graphics_color("final.scrolling_text")
        # bgcolor = colors.graphics_color("default.background")

        color = (255, 255, 255)
        bgcolor = (0, 0, 0)

        scroll_text = "W: {} {}-{} L: {} {}-{}".format(
            self.game.winning_pitcher,
            self.game.winning_pitcher_wins,
            self.game.winning_pitcher_losses,
            self.game.losing_pitcher,
            self.game.losing_pitcher_wins,
            self.game.losing_pitcher_losses,
        )

        if False and self.game.save_pitcher:
            scroll_text += " SV: {} ({})".format(self.game.save_pitcher, self.game.save_pitcher_saves)

        # TODO: Playoffs
        # if is_playoffs:
        #     scroll_text += "   " + self.game.series_status

        # return scrollingtext.render_text(
        #     canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, scroll_text, text_pos
        # )
