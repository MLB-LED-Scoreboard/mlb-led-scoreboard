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

    # Offset to the center for wider screens
    # Add a little extra separation between the bases
    offset = 0
    if self.canvas.width > 32:
    	offset = ((self.canvas.width - 32) / 2) - 2

    graphics.DrawText(self.canvas, self.font, 1 + offset, 23, pitches_color, str(self.pitches.balls) + '-' + str(self.pitches.strikes))
