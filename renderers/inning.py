from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard
from data.inning import Inning

# Because normal games are 9 innings, silly
NORMAL_GAME_LENGTH = 9

class InningRenderer:
  """Renders the inning and inning arrow on the scoreboard."""

  def __init__(self, canvas, inning, data):
    self.canvas = canvas
    self.inning = inning
    self.layout = data.config.layout
    self.colors = data.config.scoreboard_colors

  def render(self):
    if self.inning.state == Inning.TOP or self.inning.state == Inning.BOTTOM:
      self.__render_number()
      self.__render_inning_half()
    else:
      self.__render_inning_break()

  def __render_number(self):
    number_color = self.colors.graphics_color("inning.number")
    coords = self.layout.coords("inning.number")
    font = self.layout.font("inning.number")
    pos_x = coords["x"] - (len(str(self.inning.number)) * font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], pos_x, coords["y"], number_color, str(self.inning.number))

  def __render_inning_half(self):
    font = self.layout.font("inning.number")
    num_coords = self.layout.coords("inning.number")
    arrow_coords = self.layout.coords("inning.arrow")
    inning_size = (len(str(self.inning.number)) * font["size"]["width"])
    arrow_size = arrow_coords["size"]
    if self.inning.state == Inning.TOP:
      arrow_pos_x = num_coords["x"] - inning_size + arrow_coords["up"]["x_offset"]
      arrow_pos_y = num_coords["y"] + arrow_coords["up"]["y_offset"]
      self.__render_arrow(arrow_pos_x, arrow_pos_y, arrow_size, 1)
    else:
      arrow_pos_x = num_coords["x"] - inning_size + arrow_coords["down"]["x_offset"]
      arrow_pos_y = num_coords["y"] + arrow_coords["down"]["y_offset"]
      self.__render_arrow(arrow_pos_x, arrow_pos_y, arrow_size, -1)

  def __render_inning_break(self):
    text_font = self.layout.font("inning.break.text")
    num_font = self.layout.font("inning.break.number")
    text_coords = self.layout.coords("inning.break.text")
    num_coords = self.layout.coords("inning.break.number")
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = self.inning.state
    num  = self.inning.ordinal()
    text_x = center_text_position(text, text_coords["x"], text_font["size"]["width"])
    num_x = center_text_position(num, num_coords["x"], num_font["size"]["width"])
    graphics.DrawText(self.canvas, text_font["font"], text_x, text_coords["y"], color, text)
    graphics.DrawText(self.canvas, num_font["font"], num_x, num_coords["y"], color, num)

  # direction can be -1 for down or 1 for up
  def __render_arrow(self, x, y, size, direction):
    keypath = "inning.arrow.up" if direction == 1 else "inning.arrow.down"
    color = self.colors.graphics_color(keypath)
    for offset in range(size):
      graphics.DrawLine(self.canvas, x - offset, y + (offset * direction), x + offset, y + (offset * direction), color)
