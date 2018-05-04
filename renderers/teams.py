from rgbmatrix import graphics
from utils import get_font, get_file
import json

class TeamsRenderer:
  """Renders the scoreboard team banners including background color, team abbreviation text,
  and their scored runs."""

  def __init__(self, canvas, home_team, away_team, data):
    self.canvas = canvas
    self.home_team = home_team
    self.away_team = away_team
    self.data = data
    self.default_colors = self.data.config.team_colors.color("default")

  def __team_colors(self, team_abbrev):
    try:
      team_colors = self.data.config.team_colors.color(team_abbrev.lower())
    except KeyError as e:
      team_colors = self.data.config.team_colors.color("default")
    return team_colors

  def render(self):
    away_colors = self.__team_colors(self.away_team.abbrev)
    away_team_color = away_colors['home']

    home_colors = self.__team_colors(self.home_team.abbrev)
    home_team_color = home_colors['home']

    bg_coords = {}
    bg_coords["away"] = self.data.config.layout.coords("teams.background.away")
    bg_coords["home"] = self.data.config.layout.coords("teams.background.home")

    away_name_coords = self.data.config.layout.coords("teams.name.away")
    home_name_coords = self.data.config.layout.coords("teams.name.home")

    away_score_coords = self.data.config.layout.coords("teams.runs.away")
    home_score_coords = self.data.config.layout.coords("teams.runs.home")

    for team in ["away","home"]:
      for x in range(bg_coords[team]["width"]):
        for y in range(bg_coords[team]["height"]):
          color = away_team_color if team == "away" else home_team_color
          x_offset = bg_coords[team]["x"]
          y_offset = bg_coords[team]["y"]
          self.canvas.SetPixel(x + x_offset, y + y_offset, color['r'], color['g'], color['b'])

    self.__render_team_text(self.away_team, "away", away_colors, away_name_coords["x"], away_name_coords["y"])
    self.__render_team_text(self.home_team, "home", home_colors, home_name_coords["x"], home_name_coords["y"])
    self.__render_team_score(self.away_team.runs, "away", away_colors, away_score_coords["x"], away_score_coords["y"])
    self.__render_team_score(self.home_team.runs, "home", home_colors, home_score_coords["x"], home_score_coords["y"])

  def __render_team_text(self, team, homeaway, colors, x, y):
    text_color = colors.get('text', self.default_colors['text'])
    text_color_graphic = graphics.Color(text_color['r'], text_color['g'], text_color['b'])
    font = self.data.config.layout.font("teams.name.{}".format(homeaway))
    team_text = '{:3s}'.format(team.abbrev.upper())
    if self.data.config.display_full_team_names and self.canvas.width > 32:
      team_text = '{:13s}'.format(team.name)
    graphics.DrawText(self.canvas, font["font"], x, y, text_color_graphic, team_text)

  def __render_team_score(self, runs, homeaway, colors, x, y):
    text_color = colors.get('text', self.default_colors['text'])
    text_color_graphic = graphics.Color(text_color['r'], text_color['g'], text_color['b'])
    coords = self.data.config.layout.coords("teams.runs.{}".format(homeaway))
    font = self.data.config.layout.font("teams.runs.{}".format(homeaway))
    team_runs = str(runs)
    team_runs_x = coords["x"] - (len(team_runs) * font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], team_runs_x, y, text_color_graphic, team_runs)
