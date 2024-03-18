from driver import graphics

from screens.games.base import GameScreen
from screens.components.base import Base
from screens.components.out import Out
from presenters.live_game import LiveGamePresenter

from utils.text import ScrollingText

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

        # Scrollers should render first to avoid masking each other.
        self.__render_at_bat(presenter)

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
        text = presenter.count_text()
        font, font_size = self.layout.font_for("batter_count")
        coords = self.layout.coords("batter_count")
        color = self.colors.graphics_color("batter_count")
        
        graphics.DrawText(self.canvas, font, coords.x, coords.y, color, text)

    def __render_at_bat(self, presenter):
        # Pitcher
        self.__render_pitcher_text(presenter)
        self.__render_pitch_text(presenter)
        self.__render_pitch_count()

        # Batter
        self.__render_batter_text()

    def __render_pitcher_text(self, presenter):
        text = presenter.pitcher_text()
        coords = self.layout.coords("atbat.pitcher")
        color = self.colors.graphics_color("atbat.pitcher")
        font, font_size = self.layout.font_for("atbat.pitcher")
        bgcolor = self.colors.graphics_color("default.background")

        label = "P:"

        scroller = self.create_cached_object(
            "pitcher_text_scroller",
            ScrollingText,
            self.canvas,
            coords.x + font_size[0] * len(label),
            coords.y,
            coords.width,
            font,
            font_size,
            color,
            bgcolor,
            text,
            center=False
        )
        scroller.render_text()

        # Pitcher label
        graphics.DrawText(self.canvas, font, coords.x, coords.y, color, label)

    def __render_pitch_text(self, presenter):
        text = presenter.pitch_text()

        if text is None:
            return

        coords = self.layout.coords("atbat.pitch")
        color = self.colors.graphics_color("atbat.pitch")
        font, font_size = self.layout.font("atbat.pitch")

        graphics.DrawText(self.canvas, font, coords.x, coords.y, color, text)

    def __render_pitch_count(self):
        coords = self.layout.coords("atbat.pitch_count")
        color = self.colors.graphics_color("atbat.pitch_count")
        font, font_size = self.layout.font_for("atbat.pitch_count")

        if coords.enabled and not coords.append_pitcher_name:
            pitch_count = f"{self.game.pitches().pitch_count}P"
            graphics.DrawText(self.canvas, font, coords.x, coords.y, color, pitch_count)

    def __render_batter_text(self):
        coords = self.layout.coords("atbat.batter")
        color = self.colors.graphics_color("atbat.batter")
        font, font_size = self.layout.font_for("atbat.batter")
        bgcolor = self.colors.graphics_color("default.background")
        # TODO: There's an offset to the starting position here for some reason in the old code, but only on certain layouts?
        # offset = coords._asdict().get("offset", 0)

        label = "AB:"

        scroller = self.create_cached_object(
            "batter_text_scroller",
            ScrollingText,
            self.canvas,
            coords.x + font_size[0] * len(label),
            coords.y,
            coords.width,
            font,
            font_size,
            color,
            bgcolor,
            self.game.batter(),
            center=False
        )
        scroller.render_text()

        graphics.DrawText(self.canvas, font, coords.x, coords.y, color, label)
