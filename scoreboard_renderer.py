import json
from pprint import pprint

class ScoreboardRenderer:
  def __init__(self, matrix, scoreboard):
    self.matrix = matrix
    self.scoreboard = scoreboard

  def render_away_team(self):
    team_color_data = json.load(open('Assets/colors.json'))[self.scoreboard.game_data['away_team'].lower()]
    color = team_color_data['home']
    for x in range(self.matrix.width):
      for y in range(7):
        self.matrix.SetPixel(x, y, color['r'], color['g'], color['b'])
