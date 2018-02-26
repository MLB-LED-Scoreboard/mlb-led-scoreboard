from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard

# Because normal games are 9 innings, silly
NORMAL_GAME_LENGTH = 9

# Inning states
BOTTOM = 'Bottom'
END = 'End'
MIDDLE = 'Middle'
TOP = 'Top'

class InningRenderer:
  """Renders the inning and inning arrow on the scoreboard."""

  def __init__(self, canvas, inning):
    self.canvas = canvas
    self.inning = inning
    self.font = get_font()

  def render(self):
    number_color = graphics.Color(*ledcolors.scoreboard.text)
    pos_x = 28 if self.inning.number <= NORMAL_GAME_LENGTH else 24
    graphics.DrawText(self.canvas, self.font, pos_x, 20, number_color, str(self.inning.number))

    self.__render_inning_half()

  def __render_inning_half(self):
    tri_px = {'x': 24, 'y': 16}
    if self.inning.number > NORMAL_GAME_LENGTH:
      tri_px['x'] = 20

    offset = 2
    for x in range(-offset, offset + 1):
      self.canvas.SetPixel(tri_px['x'] + x, tri_px['y'], *ledcolors.scoreboard.text)

    offset = 1 if self.inning.state == BOTTOM else -1
    self.canvas.SetPixel(tri_px['x'] - 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'] + 1, tri_px['y'] + offset, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(tri_px['x'], tri_px['y'] + offset + offset, *ledcolors.scoreboard.text)
