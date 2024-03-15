from driver import graphics

from screens.games.base import GameScreen

from presenters.pregame import PregamePresenter

from utils.text import ScrollingText, CenteredText


class PregameScreen(GameScreen):
    MAX_DURATION_SECONDS = 5

    def render(self):
        presenter = self.create_cached_object("pregame_presenter", PregamePresenter, self.game, self.config)

        if self.game.is_warmup():
            self.__render_warmup(presenter)
        else:
            self.__render_start_time(presenter)

        self.__render_info(presenter)

        # Overlay banners
        self.away_team_banner.render()
        self.home_team_banner.render()

    def __render_start_time(self, presenter):
        text = presenter.start_time
        color = self.colors.graphics_color("pregame.start_time")
        coords = self.layout.coords("pregame.start_time")
        font, font_size = self.layout.font_for("pregame.start_time")

        center_text = self.create_cached_object(
            "pregame_start_time", CenteredText, self.canvas, coords.x, coords.y, font, font_size, color, text
        )
        center_text.render_text()

    def __render_warmup(self, presenter):
        text = presenter.status
        color = self.colors.graphics_color("pregame.warmup_text")
        coords = self.layout.coords("pregame.warmup_text")
        font, font_size = self.layout.font_for("pregame.warmup_text")

        center_text = self.create_cached_object(
            "pregame_start_time", CenteredText, self.canvas, coords.x, coords.y, font, font_size, color, text
        )
        center_text.render_text()

    def __render_info(self, presenter):
        text = presenter.pregame_info()

        coords = self.layout.coords("pregame.scrolling_text")
        font, font_size = self.layout.font_for("pregame.scrolling_text")

        color = self.colors.graphics_color("pregame.scrolling_text")
        bgcolor = self.colors.graphics_color("default.background")

        scroller = self.create_cached_object(
            "pregame_scroller",
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

        # TODO: This can be better, but for now this screen is done when the text is gone.
        if scroller.finished:
            self.data.schedule.request_next_game()
