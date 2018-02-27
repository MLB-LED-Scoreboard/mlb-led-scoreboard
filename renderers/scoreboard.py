from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamsRenderer
from data.inning import Inning

class Scoreboard:
  def __init__(self, canvas, scoreboard):
    self.canvas = canvas
    self.scoreboard = scoreboard

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team).render()
    InningRenderer(self.canvas, self.scoreboard.inning).render()

    if self.scoreboard.inning.state == Inning.TOP or self.scoreboard.inning.state == Inning.BOTTOM:
      PitchesRenderer(self.canvas, self.scoreboard.pitches).render()
      OutsRenderer(self.canvas, self.scoreboard.outs).render()
      BasesRenderer(self.canvas, self.scoreboard.bases).render()
