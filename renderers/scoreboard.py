from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamsRenderer

class Scoreboard:
  def __init__(self, canvas, scoreboard):
    self.canvas = canvas
    self.scoreboard = scoreboard

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team).render()
    InningRenderer(self.canvas, self.scoreboard.inning).render()

    # TODO: Don't render these if the inning state isn't top or bottom
    # Render a Final or End/Middle of Inning instead
    PitchesRenderer(self.canvas, self.scoreboard.pitches).render()
    OutsRenderer(self.canvas, self.scoreboard.outs).render()
    BasesRenderer(self.canvas, self.scoreboard.bases).render()
