from rgbmatrix import graphics
from utils import get_font, center_text_position
from data.data import Data
import debug
import time
from datetime import datetime
from time import strftime

class OffdayRenderer:
  def __init__(self, matrix, canvas, data):
    self.matrix = matrix
    self.canvas = canvas
    self.data = data
    debug.log(self)

  def render(self):
    font = get_font()
    text_color = graphics.Color(255, 235, 59)
    #text_color = self.data.config.scoreboard_colors.color("default.text")
    #background_color = self.data.config.scoreboard_colors.color("default.background")
    if self.canvas.width > 32:
      long_word = 'scheduled'
    else:
      long_word = 'today'
    
    while True:
      time_now = strftime("%-I:%M %p") 
      #self.canvas.Fill(background_color["r"], color["g"], color["b"])
      self.canvas.Fill(0, 0, 0)

      no_games_text = 'No games'
      no_games_x = center_text_position(no_games_text, self.canvas.width/2, 4)
      graphics.DrawText(self.canvas, font, no_games_x, 8, text_color, no_games_text)

      today_text = long_word
      today_x = center_text_position(today_text, self.canvas.width/2, 4)
      graphics.DrawText(self.canvas, font, today_x, 15, text_color, today_text)

      time_text = time_now
      time_x = center_text_position(time_text, self.canvas.width/2, 4)
      graphics.DrawText(self.canvas, font, time_x, 26, text_color, time_text)

      self.matrix.SwapOnVSync(self.canvas)
      time.sleep(15)

      self.canvas.Clear()
      pass # I hate the offseason and off days.

  def __str_(self):
    s = "<{} {}> Date: {}".format(self.__class__.__name__, hex(id(self)), self.data.date())
    return s