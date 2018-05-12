from PIL import Image
from rgbmatrix import graphics
from utils import get_font, get_file
import time

class StandingsRenderer:
  def __init__(self, matrix, canvas, data):
    self.matrix = matrix
    self.canvas = canvas
    self.data = data
    self.colors = data.config.scoreboard_colors
    self.bg_color = self.colors.color("standings.background")
    self.divider_color = self.colors.color("standings.divider")
    self.stat_color = self.colors.graphics_color("standings.stat")
    self.team_stat_color = self.colors.graphics_color("standings.team.stat")
    self.team_name_color = self.colors.graphics_color("standings.team.name")

  def render(self):
    self.canvas.Fill(self.bg_color["r"], self.bg_color["g"], self.bg_color["b"])

    if self.__is_dumpster_fire():
      self.__render_dumpster_fire()
    else:
      if self.canvas.width > 32:
        self.__render_static_wide_standings()
      else:
        self.__render_rotating_standings()

  def __render_rotating_standings(self):
    coords = self.data.config.layout.coords("standings")
    font = self.data.config.layout.font("standings")
    stat = 'w'
    starttime = time.time()
    while True:
      offset = coords["offset"]
      graphics.DrawText(self.canvas, font["font"], coords["stat_title"]["x"], offset, self.stat_color, stat.upper())
      for team in self.data.standings_for_preferred_division().teams:
        abbrev = '{:3s}'.format(team.team_abbrev)
        team_text = '%s' % abbrev
        stat_text = '%s' % getattr(team, stat)
        graphics.DrawText(self.canvas, font["font"], coords["team"]["name"]["x"], offset, self.team_name_color, team_text)
        graphics.DrawText(self.canvas, font["font"], coords["team"]["stat"]["x"], offset, self.team_stat_color, stat_text)

        for x in range(0, coords["width"]):
          self.canvas.SetPixel(x, offset, self.divider_color["r"], self.divider_color["g"], self.divider_color["b"])
        for y in range(0, coords["height"]):
          self.canvas.SetPixel(coords["divider"]["x"], y, self.divider_color["r"], self.divider_color["g"], self.divider_color["b"])
        offset += coords["offset"]

      self.matrix.SwapOnVSync(self.canvas)
      time.sleep(5.0)

      self.canvas.Fill(self.bg_color["r"], self.bg_color["g"], self.bg_color["b"])
      stat = 'w' if stat == 'l' else 'l'

  def __render_static_wide_standings(self):
    coords = self.data.config.layout.coords("standings")
    font = self.data.config.layout.font("standings")
    while True:
      offset = coords["offset"]

      for team in self.data.standings_for_preferred_division().teams:
        team_text = team.team_abbrev
        graphics.DrawText(self.canvas, font["font"], coords["team"]["name"]["x"], offset, self.team_name_color, team_text)

        team_record = str(team.w) + "-" + str(team.l)
        stat_text = '{:6s} {:4s}'.format(team_record, str(team.gb))
        stat_text_x = self.canvas.width - (len(stat_text) * font["size"]["width"])
        graphics.DrawText(self.canvas, font["font"], stat_text_x, offset, self.team_stat_color, stat_text)

        for x in range(0, coords["width"]):
          self.canvas.SetPixel(x, offset, self.divider_color["r"], self.divider_color["g"], self.divider_color["b"])
        for y in range(0, coords["height"]):
          self.canvas.SetPixel(coords["divider"]["x"], y, self.divider_color["r"], self.divider_color["g"], self.divider_color["b"])
        offset += coords["offset"]

        self.matrix.SwapOnVSync(self.canvas)

      time.sleep(20.0)

  def __is_dumpster_fire(self):
    return "comedy" in self.data.config.preferred_division.lower()

  def __render_dumpster_fire(self):
    image_file = get_file("Assets/fire.jpg")
    image = Image.open(image_file)
    image_rgb = image.convert("RGB")
    image_x = (self.canvas.width / 2) - 16

    self.matrix.Clear()
    while True:
      self.matrix.SetImage(image_rgb, image_x, 0)
      time.sleep(20.0)
