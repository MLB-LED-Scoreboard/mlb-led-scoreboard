from rgbmatrix import graphics
from utils import get_font
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

    graphics.DrawText(self.canvas, self.font, 1, 6, self.text_color, away_text)
    graphics.DrawText(self.canvas, self.font, 15, 6, self.text_color, '@')
    graphics.DrawText(self.canvas, self.font, 20, 6, self.text_color, home_text)

  def __render_start_time(self):
    time_text = '{:7s}'.format(self.game.start_time)
    graphics.DrawText(self.canvas, self.font, 5, 13, self.text_color, time_text)

  def __render_probable_starters(self):
    pitchers_text = self.game.away_starter + ' vs ' + self.game.home_starter
    return graphics.DrawText(self.canvas, self.font, self.probable_starter_pos, 25, self.text_color, pitchers_text)
