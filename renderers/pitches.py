from ledcoords import r32c32
from rgbmatrix import graphics
from utils import get_font
import ledcolors.scoreboard

class PitchesRenderer:
  def __init__(self, canvas, at_bat):
    self.canvas = canvas
    self.at_bat = at_bat
    self.font = get_font()

  def render(self):
    pitches_color = graphics.Color(*ledcolors.scoreboard.text)
    pitches_text = str(self.at_bat['balls']) + '-' + str(self.at_bat['strikes'])
    graphics.DrawText(self.canvas, self.font, r32c32.PITCHES_X, r32c32.PITCHES_Y, pitches_color, pitches_text)
