from ledcoords import r32c32
from rgbmatrix import graphics
from utils import get_font, get_team_colors

class TeamRenderer:
  def __init__(self, canvas, home_team, away_team, home_team_runs, away_team_runs):
    self.canvas = canvas
    self.home_team = home_team
    self.home_team_runs = home_team_runs
    self.away_team = away_team
    self.away_team_runs = away_team_runs
    self.font = get_font()
    self.colors = get_team_colors()

  def render(self):
    self.__render_team_colors()
    self.__render_team_text()

  def __render_team_colors(self):
    away_team_color_data = self.__team_color_data(self.away_team)
    away_team_color = away_team_color_data['home']

    home_team_color_data = self.__team_color_data(self.home_team)
    home_team_color = home_team_color_data['home']

    for x in range(self.canvas.width):
      for y in range(r32c32.TEAM_BANNER_HEIGHT):
        color = home_team_color if y >= r32c32.TEAM_BANNER_HEIGHT / 2 else away_team_color
        self.canvas.SetPixel(x, y, color['r'], color['g'], color['b'])

  def __render_team_text(self):
    away_team = self.away_team
    away_team_color_data = self.__team_color_data(away_team)
    away_text_color = away_team_color_data.get('text', self.colors['default']['text'])
    away_text_color_graphic = graphics.Color(away_text_color['r'], away_text_color['g'], away_text_color['b'])
    away_text = '{:3s}'.format(away_team.upper()) + ' ' + str(self.away_team_runs)

    home_team = self.home_team
    home_team_color_data = self.__team_color_data(home_team)
    home_text_color = home_team_color_data.get('text', self.colors['default']['text'])
    home_text_color_graphic = graphics.Color(home_text_color['r'], home_text_color['g'], home_text_color['b'])
    home_text = '{:3s}'.format(home_team.upper()) + ' ' + str(self.home_team_runs)

    graphics.DrawText(self.canvas, self.font, r32c32.AWAY_TEAM_NAME_X, r32c32.AWAY_TEAM_NAME_Y, away_text_color_graphic, away_text)
    graphics.DrawText(self.canvas, self.font, r32c32.HOME_TEAM_X, r32c32.HOME_TEAM_Y, home_text_color_graphic, home_text)

  def __team_color_data(self, team_name):
    return self.colors.get(team_name.lower(), self.colors['default'])
