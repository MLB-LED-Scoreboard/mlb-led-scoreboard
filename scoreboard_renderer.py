import json
from pprint import pprint
from rgbmatrix import graphics

class ScoreboardRenderer:
  def __init__(self, matrix, scoreboard):
    self.matrix = matrix
    self.scoreboard = scoreboard
    self.colors = json.load(open('Assets/colors.json'))

  def render_team_colors(self):
    away_team_color_data = self.colors[self.scoreboard.game_data['away_team'].lower()]
    away_team_color = away_team_color_data['home']

    home_team_color_data = self.colors[self.scoreboard.game_data['home_team'].lower()]
    home_team_color = home_team_color_data['home']

    for x in range(self.matrix.width):
      for y in range(14):
        color = home_team_color if y >= 7 else away_team_color
        self.matrix.SetPixel(x, y, color['r'], color['g'], color['b'])

  def render_team_text(self):
    away_team = self.scoreboard.game_data['away_team']
    away_team_color_data = self.colors[away_team.lower()]
    away_team_text_color = away_team_color_data.get('text', {'r': 255, 'g': 255, 'b': 255})
    away_text_color = graphics.Color(away_team_text_color['r'], away_team_text_color['g'], away_team_text_color['b'])

    home_team = self.scoreboard.game_data['home_team']
    home_team_color_data = self.colors[home_team.lower()]
    home_team_text_color = home_team_color_data.get('text', {'r': 255, 'g': 255, 'b': 255})
    home_text_color = graphics.Color(home_team_text_color['r'], home_team_text_color['g'], home_team_text_color['b'])

    font = graphics.Font()
    font.LoadFont('Assets/tom-thumb.bdf')
    graphics.DrawText(self.matrix, font, 1, 6, away_text_color, away_team.upper() + ' ' + str(self.scoreboard.game_data['at_bat']['away_team_runs']))
    graphics.DrawText(self.matrix, font, 1, 13, home_text_color, home_team.upper() + ' ' + str(self.scoreboard.game_data['at_bat']['home_team_runs']))
