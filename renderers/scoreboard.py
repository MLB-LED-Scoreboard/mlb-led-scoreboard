from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamsRenderer
from data.inning import Inning

class Scoreboard:
  def __init__(self, canvas, scoreboard, config):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.config = config

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.config).render()
    InningRenderer(self.canvas, self.scoreboard.inning, self.config.layout["inning"]).render()

    if self.scoreboard.inning.state == Inning.TOP or self.scoreboard.inning.state == Inning.BOTTOM:
      coords = self.config.layout
      PitchesRenderer(self.canvas, self.scoreboard.pitches, coords["batter_count"]).render()
      OutsRenderer(self.canvas, self.scoreboard.outs, coords["outs"]).render()
      BasesRenderer(self.canvas, self.scoreboard.bases, coords["bases"]).render()
