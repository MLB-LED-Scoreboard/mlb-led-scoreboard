from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard
from data.inning import Inning

# Because normal games are 9 innings, silly
NORMAL_GAME_LENGTH = 9

class InningRenderer:
  """Renders the inning and inning arrow on the scoreboard."""

  def __init__(self, canvas, inning):
    self.canvas = canvas
    self.inning = inning
    self.font = get_font()

  def render(self):
    if self.inning.state == Inning.TOP or self.inning.state == Inning.BOTTOM:
      self.__render_number()
      self.__render_inning_half()
    else:
      self.__render_inning_break()

  def __render_number(self):
    number_color = graphics.Color(*ledcolors.scoreboard.text)
    pos_x = 28 if self.inning.number <= NORMAL_GAME_LENGTH else 24
    graphics.DrawText(self.canvas, self.font, pos_x, 20, number_color, str(self.inning.number))

  def __render_inning_half(self):
    tri_px = {'x': 24, 'y': 16}
    if self.inning.number > NORMAL_GAME_LENGTH:
      tri_px['x'] = 20

    offset = 2
    for x in range(-offset, offset + 1):
      self.canvas.SetPixel(tri_px['x'] + x, tri_px['y'], *ledcolors.scoreboard.text)

    offset = 1 if self.inning.state == Inning.BOTTOM else -1
    self.canvas.SetPixel(tri_px['x'] - 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'] + 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset + offset, *ledcolors.scoreboard.text)

  def __render_inning_break(self):
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = self.inning.state
    num  = self.inning.ordinal()
    text_x = self.__center_text_pos(text, 32)
    num_x = self.__center_text_pos(num, 32)
    graphics.DrawText(self.canvas, self.font, text_x, 22, color, text)
    graphics.DrawText(self.canvas, self.font, num_x, 29, color, num)

  def __center_text_pos(self, text, canvas_width):
    return ((canvas_width - (len(text) * 4)) / 2)
