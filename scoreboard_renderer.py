import json
from pprint import pprint

class ScoreboardRenderer:
  def __init__(self, matrix, scoreboard):
    self.matrix = matrix
    self.scoreboard = scoreboard

  def render_team_colors(self):
    colors = json.load(open('Assets/colors.json'))

    away_team_color_data = colors[self.scoreboard.game_data['away_team'].lower()]
    away_team_color = away_team_color_data['home']

    home_team_color_data = colors[self.scoreboard.game_data['home_team'].lower()]
    home_team_color = home_team_color_data['home']

    for x in range(self.matrix.width):
      for y in range(14):
        color = home_team_color if y >= 7 else away_team_color
        self.matrix.SetPixel(x, y, color['r'], color['g'], color['b'])
