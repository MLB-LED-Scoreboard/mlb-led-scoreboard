from data.scoreboard.inning import Inning
from renderers.atbat import AtBatRenderer
from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.network import NetworkErrorRenderer
from renderers.nohitter import NoHitterRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamsRenderer


class Scoreboard:
    def __init__(self, canvas, scoreboard, data, text_pos, animation_time):
        self.canvas = canvas
        self.scoreboard = scoreboard
        self.data = data
        self.start_pos = text_pos
        self.animation_time = animation_time

    def render(self):
        pos = 0
        if self.scoreboard.inning.state == Inning.TOP or self.scoreboard.inning.state == Inning.BOTTOM:

            pos = AtBatRenderer(
                self.canvas,
                self.scoreboard.atbat,
                self.data,
                self.start_pos,
                self.scoreboard.strikeout(),
                self.animation_time,
            ).render()

            # Check if we're deep enough into a game and it's a no hitter or perfect game
            should_display_nohitter = self.data.config.layout.coords("nohitter")["innings_until_display"]
            if self.scoreboard.inning.number > should_display_nohitter:
                if self.data.config.layout.state_is_nohitter():
                    NoHitterRenderer(self.canvas, self.data).render()
            PitchesRenderer(self.canvas, self.scoreboard.pitches, self.data).render()
            OutsRenderer(self.canvas, self.scoreboard.outs, self.data).render()
            BasesRenderer(
                self.canvas, self.scoreboard.bases, self.data, self.scoreboard.homerun(), self.animation_time % 16
            ).render()

        TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.data).render()
        InningRenderer(self.canvas, self.scoreboard.inning, self.data, self.scoreboard.atbat).render()
        NetworkErrorRenderer(self.canvas, self.data).render()
        return pos
