from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamsRenderer
from renderers.nohitter import NoHitterRenderer
from data.inning import Inning
from data.layout import Layout
import data.layout

class Scoreboard:
  def __init__(self, canvas, scoreboard, data):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.data = data

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.data).render()
    InningRenderer(self.canvas, self.scoreboard.inning, self.data).render()

    if self.scoreboard.inning.state == Inning.TOP or self.scoreboard.inning.state == Inning.BOTTOM:

      # Check if we're deep enough into a game and it's a no hitter or perfect game
      should_display_nohitter = self.data.config.layout.coords("nohitter")["innings_until_display"]
      if self.scoreboard.inning.number > should_display_nohitter:
        if self.data.config.layout.state_is_nohitter():
          NoHitterRenderer(self.canvas, self.data).render()

      PitchesRenderer(self.canvas, self.scoreboard.pitches, self.data).render()
      OutsRenderer(self.canvas, self.scoreboard.outs, self.data).render()
      BasesRenderer(self.canvas, self.scoreboard.bases, self.data).render()
