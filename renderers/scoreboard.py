from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamsRenderer
from data.inning import Inning

class Scoreboard:
  def __init__(self, canvas, scoreboard, coords):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.coords = coords

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.coords["teams"]).render()
    InningRenderer(self.canvas, self.scoreboard.inning, self.coords["inning"]).render()

    if self.scoreboard.inning.state == Inning.TOP or self.scoreboard.inning.state == Inning.BOTTOM:
      PitchesRenderer(self.canvas, self.scoreboard.pitches, self.coords["pitches"]).render()
      OutsRenderer(self.canvas, self.scoreboard.outs, self.coords["outs"]).render()
      BasesRenderer(self.canvas, self.scoreboard.bases, self.coords["bases"]).render()
