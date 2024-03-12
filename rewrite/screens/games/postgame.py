from driver import graphics

from screens.games.base import GameScreen

from presenters.postgame import PostgamePresenter

from utils.text import ScrollingText, CenteredText


class PostgameScreen(GameScreen):
    MAX_DURATION_SECONDS = 5

    def render(self):
        presenter = self.create_cached_object("postgame_presenter", PostgamePresenter, self.game)

        self.__render_final_inning(presenter)
        self.__render_decision_scroll(presenter)

    def __render_final_inning(self, presenter):
        text = "FINAL"
        color = self.colors.graphics_color("final.inning")
        coords = self.layout.coords("final.inning")
        font, font_size = self.layout.font_for("final.inning")

        # TODO: No concept of a "scoreboard" yet
        # if scoreboard.inning.number != NORMAL_GAME_LENGTH:
        #     text += " " + str(scoreboard.inning.number)

        center_text = self.create_cached_object(
            "postgame_center_text", CenteredText, self.canvas, coords.x, coords.y, font, font_size, color, text
        )
        center_text.render_text()

        # TODO: Handle no-hitters
        # if layout.state_is_nohitter():
        #     nohit_text = nohitter._get_nohitter_text(layout)
        #     nohit_coords = layout.coords("final.nohit_text")
        #     nohit_color = colors.graphics_color("final.nohit_text")
        #     nohit_font = layout.font("final.nohit_text")
        #     graphics.DrawText(canvas, nohit_font["font"], nohit_coords["x"], nohit_coords["y"], nohit_color, nohit_text)

    def __render_decision_scroll(self, presenter):
        coords = self.layout.coords("final.scrolling_text")
        font, font_size = self.layout.font_for("final.scrolling_text")

        color = self.colors.graphics_color("final.scrolling_text")
        bgcolor = self.colors.graphics_color("default.background")

        text = "W: {} {}-{} L: {} {}-{}".format(
            presenter.winning_pitcher,
            presenter.winning_pitcher_wins,
            presenter.winning_pitcher_losses,
            presenter.losing_pitcher,
            presenter.losing_pitcher_wins,
            presenter.losing_pitcher_losses,
        )

        if presenter.save_pitcher:
            scroll_text += " SV: {} ({})".format(self.game.save_pitcher, self.game.save_pitcher_saves)

        # TODO: Playoffs
        # if is_playoffs:
        #     scroll_text += "   " + self.game.series_status

        # return scrollingtext.render_text(
        #     canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, scroll_text, text_pos
        # )

        scroller = self.create_cached_object(
            "postgame_scroller",
            ScrollingText,
            self.canvas,
            coords.x,
            coords.y,
            coords.width,
            coords.width,
            font,
            font_size,
            color,
            bgcolor,
            text,
        )
        scroller.render_text()
