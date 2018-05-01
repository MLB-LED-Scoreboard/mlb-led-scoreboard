from data.status import Status
from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard

class Pregame:
  def __init__(self, canvas, game, coords, probable_starter_pos):
    self.canvas = canvas
    self.game = game
    self.coords = coords
    self.font = get_font()
    self.text_color = graphics.Color(*ledcolors.scoreboard.text)
    self.probable_starter_pos = probable_starter_pos


  def render(self):
    self.__render_matchup()
    self.__render_start_time()
    if self.game.status == Status.WARMUP:
      self.__render_warmup()
    return self.__render_probable_starters()

  def __render_matchup(self):
    away_text = '{:>3s}'.format(self.game.away_team)
    home_text = '{:3s}'.format(self.game.home_team)
    teams_text = "{}  {}".format(away_text, home_text)
    teams_text_x = center_text_position(teams_text, self.coords["matchup"]["x"])
    at_x = center_text_position("@", self.coords["matchup"]["x"])
    graphics.DrawText(self.canvas, self.font, teams_text_x, self.coords["matchup"]["y"], self.text_color, teams_text)
    graphics.DrawText(self.canvas, self.font, at_x, self.coords["matchup"]["y"], self.text_color, "@")

  def __render_start_time(self):
    time_text = self.game.start_time
    time_x = center_text_position(time_text, self.coords["start_time"]["x"])
    graphics.DrawText(self.canvas, self.font, time_x, self.coords["start_time"]["y"], self.text_color, time_text)

  def __render_warmup(self):
    warmup_text = self.game.status
    warmup_x = center_text_position(warmup_text, self.coords["warmup_text"]["x"])
    graphics.DrawText(self.canvas, self.font, warmup_x, self.coords["warmup_text"]["y"], self.text_color, warmup_text)

  def __render_probable_starters(self):
    coords = self.coords["scrolling_text"]
    pitchers_y = coords["warmup"]["y"] if self.game.status == Status.WARMUP else coords["y"]
    pitchers_text = self.game.away_starter + ' vs ' + self.game.home_starter
    return graphics.DrawText(self.canvas, self.font, self.probable_starter_pos, pitchers_y, self.text_color, pitchers_text)
