from rgbmatrix import graphics
from utils import get_font
import ledcolors.standings
import time

class StandingsRenderer:
  def __init__(self, matrix, canvas, data):
    self.matrix = matrix
    self.canvas = canvas
    self.data = data

  def render(self):
    font = get_font()
    text_color = graphics.Color(*ledcolors.standings.text)

    self.canvas.Fill(*ledcolors.standings.fill)

    if self.canvas.width > 32:
      self.__render_static_wide_standings(font, text_color)
    else:
      self.__render_rotating_standings(font, text_color)

  def __render_rotating_standings(self, font, text_color):
    stat = 'w'
    starttime = time.time()
    while True:
      offset = 6
      graphics.DrawText(self.canvas, font, self.data.config.coords["standings"]["stat"]["x"], offset, text_color, stat.upper())
      for team in self.data.standings_for_preferred_division().teams:
        abbrev = '{:3s}'.format(team.team_abbrev)
        team_text = '%s' % abbrev
        stat_text = '%s' % getattr(team, stat)
        graphics.DrawText(self.canvas, font, self.data.config.coords["standings"]["team"]["name"]["x"], offset, text_color, team_text)
        graphics.DrawText(self.canvas, font, self.data.config.coords["standings"]["team"]["stat"]["x"], offset, text_color, stat_text)

        for x in range(0, self.canvas.width):
          self.canvas.SetPixel(x, offset, *ledcolors.standings.divider)
        for y in range(0, self.canvas.height):
          self.canvas.SetPixel(self.data.config.coords["standings"]["divider"]["x"], y, *ledcolors.standings.divider)
        offset += 6

      self.matrix.SwapOnVSync(self.canvas)
      time.sleep(5.0)

      self.canvas.Fill(*ledcolors.standings.fill)
      stat = 'w' if stat == 'l' else 'l'

  def __render_static_wide_standings(self, font, text_color):
    while True:
      offset = 6

      for team in self.data.standings_for_preferred_division().teams:
        team_text = team.team_abbrev
        graphics.DrawText(self.canvas, font, self.data.config.coords["standings"]["team"]["x"], offset, text_color, team_text)

        team_record = str(team.w) + "-" + str(team.l)
        stat_text = '{:6s} {:4s}'.format(team_record, str(team.gb))
        stat_text_x = self.canvas.width - (len(stat_text) * 4)
        graphics.DrawText(self.canvas, font, stat_text_x, offset, text_color, stat_text)

        for x in range(0, self.canvas.width):
          self.canvas.SetPixel(x, offset, *ledcolors.standings.divider)
        for y in range(0, self.canvas.height):
          self.canvas.SetPixel(self.data.config.coords["standings"]["divider"]["x"], y, *ledcolors.standings.divider)
        offset += 6

        self.matrix.SwapOnVSync(self.canvas)

      time.sleep(20.0)
