from data.status import Status
from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard
import data.layout

class Pregame:
  def __init__(self, canvas, game, data, probable_starter_pos):
    self.canvas = canvas
    self.game = game
    self.layout = data.config.layout
    self.text_color = graphics.Color(*ledcolors.scoreboard.text)
    self.probable_starter_pos = probable_starter_pos

  def render(self):
    self.__render_matchup()
    self.__render_start_time()
    if self.layout.state == data.layout.LAYOUT_STATE_WARMUP:
      self.__render_warmup()
    return self.__render_probable_starters()

  def __render_matchup(self):
    away_text = '{:>3s}'.format(self.game.away_team)
    home_text = '{:3s}'.format(self.game.home_team)
    teams_text = "{}  {}".format(away_text, home_text)
    coords = self.layout.coords("pregame.matchup")
    font = self.layout.font("pregame.matchup")
    teams_text_x = center_text_position(teams_text, coords["x"], font["size"]["width"])
    at_x = center_text_position("@", coords["x"], font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], teams_text_x, coords["y"], self.text_color, teams_text)
    graphics.DrawText(self.canvas, font["font"], at_x, coords["y"], self.text_color, "@")

  def __render_start_time(self):
    time_text = self.game.start_time
    coords = self.layout.coords("pregame.start_time")
    font = self.layout.font("pregame.start_time")
    time_x = center_text_position(time_text, coords["x"], font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], time_x, coords["y"], self.text_color, time_text)

  def __render_warmup(self):
    warmup_text = self.game.status
    coords = self.layout.coords("pregame.warmup_text")
    font = self.layout.font("pregame.warmup_text")
    warmup_x = center_text_position(warmup_text, coords["x"], font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], warmup_x, coords["y"], self.text_color, warmup_text)

  def __render_probable_starters(self):
    coords = self.layout.coords("pregame.scrolling_text")
    font = self.layout.font("pregame.scrolling_text")
    pitchers_text = self.game.away_starter + ' vs ' + self.game.home_starter
    return graphics.DrawText(self.canvas, font["font"], self.probable_starter_pos, coords["y"], self.text_color, pitchers_text)
