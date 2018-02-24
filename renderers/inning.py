from ledcoords import r32c32
from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard

# Normal games have 9 innings of course
NUM_INNINGS = 9

class InningRenderer:
  def __init__(self, canvas, inning):
    self.canvas = canvas
    self.inning = inning
    self.font = get_font()

  def render(self):
    self.__render_inning_half()

    number = self.inning['number']
    pos_x = r32c32.INNING_NUM_X if number <= NUM_INNINGS else r32c32.INNING_NUM_X_EXTRAS
    number_color = graphics.Color(*ledcolors.scoreboard.text)
    graphics.DrawText(self.canvas, self.font, pos_x, r32c32.INNING_NUM_Y, number_color, str(number))

  def __render_inning_half(self):
    tri_px = {'x': r32c32.ARROW_X, 'y': r32c32.ARROW_Y}
    if self.inning['number'] > NUM_INNINGS:
      tri_px['x'] = r32c32.ARROW_X_EXTRAS

    offset = 2
    for x in range(-offset, offset + 1):
      self.canvas.SetPixel(tri_px['x'] + x, tri_px['y'], *ledcolors.scoreboard.text)

    offset = 1 if self.inning['bottom'] else -1
    self.canvas.SetPixel(tri_px['x'] - 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'] + 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset + offset, *ledcolors.scoreboard.text)