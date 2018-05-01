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
    batter_count_text = "{}-{}".format(self.pitches.balls, self.pitches.strikes)
    graphics.DrawText(self.canvas, self.font, self.coords["x"], self.coords["y"], pitches_color, batter_count_text)
