from rgbmatrix import graphics
from utils import get_font, center_text_position
import debug
import ledcolors.scoreboard

class OffdayRenderer:
  def __init__(self, matrix, canvas, date):
    self.matrix = matrix
    self.canvas = canvas
    self.date = date
    debug.log(self)

  def render(self):
    font = get_font()
    text_color = graphics.Color(*ledcolors.scoreboard.text)

    self.canvas.Fill(*ledcolors.scoreboard.fill)
    no_text = 'No'
    no_x = center_text_position(no_text, self.canvas.width)
    graphics.DrawText(self.canvas, font, no_x, 8, text_color, no_text)

    games_text = 'games'
    games_x = center_text_position(games_text, self.canvas.width)
    graphics.DrawText(self.canvas, font, games_x, 15, text_color, games_text)

    today_text = 'today'
    today_x = center_text_position(today_text, self.canvas.width)
    graphics.DrawText(self.canvas, font, today_x, 22, text_color, today_text)

    frown_text = ':('
    frown_x = center_text_position(frown_text, self.canvas.width)
    graphics.DrawText(self.canvas, font, frown_x, 29, text_color, frown_text)

    self.matrix.SwapOnVSync(self.canvas)

    while True:
      pass # I hate the offseason and off days.

  def __str_(self):
    s = "<%s %s> " % (self.__class__.__name__, hex(id(self)))
    s += "Date: %s" % (self.date)
    return s
