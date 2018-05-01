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
    pos_x = self.coords["number"]["x"] - (len(str(self.inning.number)) * 4)
    graphics.DrawText(self.canvas, self.font, pos_x, self.coords["number"]["y"], number_color, str(self.inning.number))

  def __render_inning_half(self):
    inning_size = (len(str(self.inning.number)) * 4)
    arrow_size = self.coords["arrow"]["size"]
    if self.inning.state == Inning.TOP:
      arrow_pos_x = self.coords["number"]["x"] - inning_size + self.coords["arrow"]["up"]["x_offset"]
      arrow_pos_y = self.coords["number"]["y"] + self.coords["arrow"]["up"]["y_offset"]
      self.__render_arrow(arrow_pos_x, arrow_pos_y, arrow_size, 1)
    else:
      arrow_pos_x = self.coords["number"]["x"] - inning_size + self.coords["arrow"]["down"]["x_offset"]
      arrow_pos_y = self.coords["number"]["y"] + self.coords["arrow"]["down"]["y_offset"]
      self.__render_arrow(arrow_pos_x, arrow_pos_y, arrow_size, -1)

  def __render_inning_break(self):
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = self.inning.state
    num  = self.inning.ordinal()
    coords = self.coords["break"]
    text_x = center_text_position(text, coords["text"]["x"])
    num_x = center_text_position(num, coords["number"]["x"])
    graphics.DrawText(self.canvas, self.font, text_x, coords["text"]["y"], color, text)
    graphics.DrawText(self.canvas, self.font, num_x, coords["number"]["y"], color, num)

  # direction can be -1 for down or 1 for up
  def __render_arrow(self, x, y, size, direction):
    color = graphics.Color(*ledcolors.scoreboard.text)
    for offset in range(size):
      graphics.DrawLine(self.canvas, x - offset, y + (offset * direction), x + offset, y + (offset * direction), color)
