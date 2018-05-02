from rgbmatrix import graphics
from utils import get_font, get_file
import json

class TeamsRenderer:
  """Renders the scoreboard team banners including background color, team abbreviation text,
  and their scored runs."""

  def __init__(self, canvas, home_team, away_team, config):
    self.canvas = canvas
    self.home_team = home_team
    self.away_team = away_team
    self.coords = config.coords["teams"]
    self.display_full_team_names = config.display_full_team_names

    self.colors = json.load(open(get_file('Assets/colors.json')))
    self.font = get_font()

  def __team_colors(self, team_abbrev):
    return self.colors.get(team_abbrev.lower(), self.colors['default'])

  def render(self):
    away_colors = self.__team_colors(self.away_team.abbrev)
    away_team_color = away_colors['home']

    home_colors = self.__team_colors(self.home_team.abbrev)
    home_team_color = home_colors['home']

    scores_height = 14
    for x in range(self.canvas.width):
      for y in range(scores_height):
        color = home_team_color if y >= scores_height / 2 else away_team_color
        self.canvas.SetPixel(x, y, color['r'], color['g'], color['b'])

    self.__render_team_text(self.away_team, away_colors, self.coords["away"]["x"], self.coords["away"]["y"])
    self.__render_team_text(self.home_team, home_colors, self.coords["home"]["x"], self.coords["home"]["y"])

  def __render_team_text(self, team, colors, x, y):
    text_color = colors.get('text', self.colors['default']['text'])
    text_color_graphic = graphics.Color(text_color['r'], text_color['g'], text_color['b'])
    team_text = '{:3s}'.format(team.abbrev.upper())
    if self.display_full_team_names and self.canvas.width > 32:
      team_text = '{:13s}'.format(team.name)
    team_runs = str(team.runs)
    team_runs_x = self.canvas.width - (len(team_runs) * 4) - 2
    graphics.DrawText(self.canvas, self.font, x, y, text_color_graphic, team_text)
    graphics.DrawText(self.canvas, self.font, team_runs_x, y, text_color_graphic, team_runs)
