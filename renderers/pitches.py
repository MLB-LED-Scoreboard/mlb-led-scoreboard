from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard

class PitchesRenderer:
  """Renders balls and strikes on the scoreboard."""

  def __init__(self, canvas, pitches, coords):
    self.canvas = canvas
    self.pitches = pitches
    self.coords = coords
    self.font = get_font()

  def render(self):
    pitches_color = graphics.Color(*ledcolors.scoreboard.text)

    # Offset to the center for wider screens
    # Add a little extra separation between the bases
    offset = 0
    if self.canvas.width > 32:
    	offset = ((self.canvas.width - 32) / 2) - 2

    graphics.DrawText(self.canvas, self.font, self.coords["x"] + offset, self.coords["y"], pitches_color, str(self.pitches.balls) + '-' + str(self.pitches.strikes))
