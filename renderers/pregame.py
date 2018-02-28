from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard

class Pregame:
  def __init__(self, canvas, game, probable_starter_pos):
    self.canvas = canvas
    self.game = game
    self.font = get_font()
    self.text_color = graphics.Color(*ledcolors.scoreboard.text)
    self.probable_starter_pos = probable_starter_pos


  def render(self):
    self.__render_matchup()
    self.__render_start_time()
    return self.__render_probable_starters()

  def __render_matchup(self):
    away_text = '{:>3s}'.format(self.game.away_team)
    home_text = '{:3s}'.format(self.game.home_team)
    teams_text = "%s  %s" % (away_text, home_text)
    teams_text_x = center_text_position(teams_text, self.canvas.width)
    at_x = center_text_position("@", self.canvas.width)
    graphics.DrawText(self.canvas, self.font, teams_text_x, 6, self.text_color, teams_text)
    graphics.DrawText(self.canvas, self.font, at_x, 6, self.text_color, "@")

  def __render_start_time(self):
    time_text = self.game.start_time
    time_x = center_text_position(time_text, self.canvas.width)
    graphics.DrawText(self.canvas, self.font, time_x, 13, self.text_color, time_text)

  def __render_probable_starters(self):
    pitchers_text = self.game.away_starter + ' vs ' + self.game.home_starter
    return graphics.DrawText(self.canvas, self.font, self.probable_starter_pos, 25, self.text_color, pitchers_text)
