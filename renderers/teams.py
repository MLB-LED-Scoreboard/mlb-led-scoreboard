from rgbmatrix import graphics
from utils import get_font, get_file
import json

class TeamsRenderer:
  """Renders the scoreboard team banners including background color, team abbreviation text,
  and their scored runs."""

  def __init__(self, canvas, home_team, away_team):
    self.canvas = canvas
    self.home_team = home_team
    self.away_team = away_team

    self.colors = json.load(open(get_file('Assets/colors.json')))
    self.font = get_font()

  def __team_colors(self, team_name):
    return self.colors.get(team_name.lower(), self.colors['default'])

  def render(self):
    away_colors = self.__team_colors(self.away_team.team_name)
    away_team_color = away_colors['home']

    home_colors = self.__team_colors(self.home_team.team_name)
    home_team_color = home_colors['home']

    scores_height = 14
    for x in range(self.canvas.width):
      for y in range(scores_height):
        color = home_team_color if y >= scores_height / 2 else away_team_color
        self.canvas.SetPixel(x, y, color['r'], color['g'], color['b'])

    self.__render_team_text(self.away_team, away_colors, 1, 6)
    self.__render_team_text(self.home_team, home_colors, 1, 13)

  def __render_team_text(self, team, colors, x, y):
    text_color = colors.get('text', self.colors['default']['text'])
    text_color_graphic = graphics.Color(text_color['r'], text_color['g'], text_color['b'])
    team_text = '{:3s}'.format(team.team_name.upper()) + ' ' + str(team.runs)
    graphics.DrawText(self.canvas, self.font, x, y, text_color_graphic, team_text)
