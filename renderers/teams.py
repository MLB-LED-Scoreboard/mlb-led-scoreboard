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
    self.name_coords = config.layout["teams"]["name"]
    self.score_coords = config.layout["teams"]["runs"]
    self.background_coords = config.layout["teams"]["background"]
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

    for team in ["away","home"]:
      for x in range(self.background_coords[team]["width"]):
        for y in range(self.background_coords[team]["height"]):
          color = away_team_color if team == "away" else home_team_color
          x_offset = self.background_coords[team]["x"]
          y_offset = self.background_coords[team]["y"]
          self.canvas.SetPixel(x + x_offset, y + y_offset, color['r'], color['g'], color['b'])

    self.__render_team_text(self.away_team, away_colors, self.name_coords["away"]["x"], self.name_coords["away"]["y"])
    self.__render_team_text(self.home_team, home_colors, self.name_coords["home"]["x"], self.name_coords["home"]["y"])
    self.__render_team_score(self.away_team.runs, "away", away_colors, self.score_coords["away"]["x"], self.score_coords["away"]["y"])
    self.__render_team_score(self.home_team.runs, "home", home_colors, self.score_coords["home"]["x"], self.score_coords["home"]["y"])

  def __render_team_text(self, team, colors, x, y):
    text_color = colors.get('text', self.colors['default']['text'])
    text_color_graphic = graphics.Color(text_color['r'], text_color['g'], text_color['b'])
    team_text = '{:3s}'.format(team.abbrev.upper())
    if self.display_full_team_names and self.canvas.width > 32:
      team_text = '{:13s}'.format(team.name)
    graphics.DrawText(self.canvas, self.font, x, y, text_color_graphic, team_text)

  def __render_team_score(self, runs, homeaway, colors, x, y):
    text_color = colors.get('text', self.colors['default']['text'])
    text_color_graphic = graphics.Color(text_color['r'], text_color['g'], text_color['b'])
    team_runs = str(runs)
    team_runs_x = self.score_coords[homeaway]["x"] - (len(team_runs) * 4)
    graphics.DrawText(self.canvas, self.font, team_runs_x, y, text_color_graphic, team_runs)
