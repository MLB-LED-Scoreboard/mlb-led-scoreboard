from PIL import Image
from rgbmatrix import graphics
from utils import get_font, get_file, center_text_position
from renderers.network import NetworkErrorRenderer
import time

class StandingsRenderer:
  def __init__(self, matrix, canvas, data):
    self.matrix = matrix
    self.canvas = canvas
    self.data = data
    self.colors = data.config.scoreboard_colors
    self.bg_color = self.colors.graphics_color("standings.background")
    self.divider_color = self.colors.graphics_color("standings.divider")
    self.stat_color = self.colors.graphics_color("standings.stat")
    self.team_stat_color = self.colors.graphics_color("standings.team.stat")
    self.team_name_color = self.colors.graphics_color("standings.team.name")

  def render(self):
    self.__fill_bg()
    if self.__is_dumpster_fire():
      self.__render_dumpster_fire()
    else:
      if self.canvas.width > 32:
        self.__render_static_wide_standings()
      else:
        self.__render_rotating_standings()
    NetworkErrorRenderer(self.canvas, self.data).render()

  def __fill_bg(self):
    coords = self.data.config.layout.coords("standings")
    for y in range(0, coords["height"]):
      graphics.DrawLine(self.canvas, 0, y, coords["width"], y, self.bg_color)

  def __render_rotating_standings(self):
    coords = self.data.config.layout.coords("standings")
    font = self.data.config.layout.font("standings")
    stat = 'w'
    starttime = time.time()
    while True:
      offset = coords["offset"]
      graphics.DrawText(self.canvas, font["font"], coords["stat_title"]["x"], offset, self.stat_color, stat.upper())
      graphics.DrawLine(self.canvas, coords["divider"]["x"], 0, coords["divider"]["x"], coords["height"], self.divider_color)

      for team in self.data.current_standings().teams:
        graphics.DrawLine(self.canvas, 0, offset, coords["width"], offset, self.divider_color)

        team_text = "{:3s}".format(team.team_abbrev)
        stat_text = str(getattr(team, stat))
        graphics.DrawText(self.canvas, font["font"], coords["team"]["name"]["x"], offset, self.team_name_color, team_text)
        graphics.DrawText(self.canvas, font["font"], coords["team"]["record"]["x"], offset, self.team_stat_color, stat_text)

        offset += coords["offset"]

      self.matrix.SwapOnVSync(self.canvas)
      time.sleep(5.0)

      self.__fill_bg()

      if stat == 'l':
        self.data.advance_to_next_standings()
        stat = 'w'
      else:
        stat = 'l'

  def __render_static_wide_standings(self):
    coords = self.data.config.layout.coords("standings")
    font = self.data.config.layout.font("standings")
    while True:
      offset = coords["offset"]
      graphics.DrawLine(self.canvas, coords["divider"]["x"], 0, coords["divider"]["x"], coords["height"], self.divider_color)

      for team in self.data.current_standings().teams:
        graphics.DrawLine(self.canvas, 0, offset, coords["width"], offset, self.divider_color)

        team_text = team.team_abbrev
        graphics.DrawText(self.canvas, font["font"], coords["team"]["name"]["x"], offset, self.team_name_color, team_text)

        record_text = "{}-{}".format(team.w, team.l)
        record_text_x = center_text_position(record_text, coords["team"]["record"]["x"], font["size"]["width"])

        if "-" in str(team.gb):
          gb_text = " -  "
        else:
          gb_text = "{:>4s}".format(str(team.gb))
        gb_text_x = coords["team"]["games_back"]["x"] - (len(gb_text) * font["size"]["width"])

        graphics.DrawText(self.canvas, font["font"], record_text_x, offset, self.team_stat_color, record_text)
        graphics.DrawText(self.canvas, font["font"], gb_text_x, offset, self.team_stat_color, gb_text)

        offset += coords["offset"]

      self.matrix.SwapOnVSync(self.canvas)
      time.sleep(10.0)
      self.__fill_bg()
      self.data.advance_to_next_standings()

  def __is_dumpster_fire(self):
    return "comedy" in self.data.config.preferred_divisions[self.data.current_division_index].lower()

  def __render_dumpster_fire(self):
    image_file = get_file("Assets/fire.jpg")
    image = Image.open(image_file)
    image_rgb = image.convert("RGB")
    image_x = (self.canvas.width / 2) - 16

    self.matrix.Clear()
    while True:
      self.matrix.SetImage(image_rgb, image_x, 0)
      time.sleep(20.0)
