from rgbmatrix import graphics
from renderers.bases import BasesRenderer
from renderers.inning import InningRenderer
from renderers.outs import OutsRenderer
from renderers.pitches import PitchesRenderer
from renderers.teams import TeamRenderer

class ScoreboardRenderer:
  def __init__(self, canvas, scoreboard):
    self.canvas = canvas
    self.scoreboard = scoreboard

  def render(self):
    inning = self.scoreboard.game_data['inning']
    InningRenderer(self.canvas, inning).render()

    at_bat = inning['at_bat']
    PitchesRenderer(self.canvas, at_bat).render()

    outs = at_bat['outs']
    OutsRenderer(self.canvas, outs).render()

    bases = at_bat['bases']
    BasesRenderer(self.canvas, at_bat['bases']).render()

    away_team_runs = at_bat['away_team_runs']
    home_team_runs = at_bat['home_team_runs']
    away_team = self.scoreboard.game_data['away_team']
    home_team = self.scoreboard.game_data['home_team']
    TeamRenderer(self.canvas, home_team, away_team, home_team_runs, away_team_runs).render()
