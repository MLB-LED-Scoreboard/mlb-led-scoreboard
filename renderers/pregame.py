from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard

class Pregame:
  def __init__(self, canvas, game):
    self.canvas = canvas
    self.game = game
    self.font = get_font()

  def render(self):
    self.__render_matchup()
    self.__render_start_time()
  
  def __render_matchup(self):
    text_color = graphics.Color(*ledcolors.scoreboard.text)
    away_text = '{:>3s}'.format(self.game.game_data['away_team'])
    home_text = '{:3s}'.format(self.game.game_data['home_team'])

    graphics.DrawText(self.canvas, self.font, 1, 6, text_color, away_text)
    graphics.DrawText(self.canvas, self.font, 15, 6, text_color, '@')
    graphics.DrawText(self.canvas, self.font, 20, 6, text_color, home_text)
  
  def __render_start_time(self):
    text_color = graphics.Color(*ledcolors.scoreboard.text)
    time_text = '{:7s}'.format(self.game.game_data['time'])
    graphics.DrawText(self.canvas, self.font, 5, 13, text_color, self.game.game_data['time'])
