from driver import graphics

from screens.games.base import GameScreen
from screens.components.base import Base
from screens.components.out import Out
from presenters.live_game import LiveGamePresenter


class LiveGameScreen(GameScreen):
    MAX_DURATION_SECONDS = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bases = [
            Base(1, self),
            Base(2, self),
            Base(3, self)
        ]

        self.outs = [
            Out(1, self),
            Out(2, self),
            Out(3, self),
        ]

    def render(self):
        presenter = self.create_cached_object("live_game_presenter", LiveGamePresenter, self.game, self.config)

        self.__render_bases()
        self.__render_outs()
        self.__render_count(presenter)

        # Overlay banners
        self.away_team_banner.render()
        self.home_team_banner.render()

    def __render_bases(self):
        for base in self.bases:
            base.render()

    def __render_outs(self):
        for out in self.outs:
            out.render()

    def __render_count(self, presenter):
        text = presenter.batter_count_text()
        font, font_size = self.layout.font_for("batter_count")
        coords = self.layout.coords("batter_count")
        color = self.colors.graphics_color("batter_count")
        
        graphics.DrawText(self.canvas, font, coords.x, coords.y, color, text)
