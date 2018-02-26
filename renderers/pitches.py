from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard

class PitchesRenderer:
  """Renders balls and strikes on the scoreboard."""

  def __init__(self, canvas, pitches):
    self.canvas = canvas
    self.pitches = pitches
    self.font = get_font()

  def render(self):
    pitches_color = graphics.Color(*ledcolors.scoreboard.text)
    graphics.DrawText(self.canvas, self.font, 1, 23, pitches_color, str(self.pitches.balls) + '-' + str(self.pitches.strikes))
