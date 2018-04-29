from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard
from data.inning import Inning

# Because normal games are 9 innings, silly
NORMAL_GAME_LENGTH = 9

class InningRenderer:
  """Renders the inning and inning arrow on the scoreboard."""

  def __init__(self, canvas, inning, coords):
    self.canvas = canvas
    self.inning = inning
    self.coords = coords
    self.font = get_font()

  def render(self):
    if self.inning.state == Inning.TOP or self.inning.state == Inning.BOTTOM:
      self.__render_number()
      self.__render_inning_half()
    else:
      self.__render_inning_break()

  def __render_number(self):
    number_color = graphics.Color(*ledcolors.scoreboard.text)
    pos_x = self.canvas.width - (len(str(self.inning.number)) * 6)
    graphics.DrawText(self.canvas, self.font, pos_x, self.coords["number"]["y"], number_color, str(self.inning.number))

  def __render_inning_half(self):
    inning_size = (len(str(self.inning.number)) * 6)
    arrow_pos = self.canvas.width - inning_size - 8
    if self.inning.state == Inning.TOP:
      self.__render_up_arrow(arrow_pos, self.coords["number"]["y"])
    else:
      self.__render_down_arrow(arrow_pos, self.coords["number"]["y"])

  def __render_inning_break(self):
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = self.inning.state
    num  = self.inning.ordinal()
    text_x = center_text_position(text, self.canvas.width)
    num_x = center_text_position(num, self.canvas.width)
    coords = self.coords["break"]
    graphics.DrawText(self.canvas, self.font, text_x, coords["text"]["y"], color, text)
    graphics.DrawText(self.canvas, self.font, num_x, coords["number"]["y"], color, num)

  # render_arrow methods now line up with the same text y position
  def __render_up_arrow(self, x, y):
    y_offset = -4
    for offset in range(0,5):
      self.canvas.SetPixel(x + offset, y + y_offset + 2, *ledcolors.scoreboard.text)
    for offset in range(1,4):
      self.canvas.SetPixel(x + offset, y + y_offset + 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(x + 2, y + y_offset, *ledcolors.scoreboard.text)

  def __render_down_arrow(self, x, y):
    y_offset = -2
    for offset in range(0,5):
      self.canvas.SetPixel(x + offset, y + y_offset - 2, *ledcolors.scoreboard.text)
    for offset in range(1,4):
      self.canvas.SetPixel(x + offset, y + y_offset - 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(x + 2, y + y_offset, *ledcolors.scoreboard.text)
