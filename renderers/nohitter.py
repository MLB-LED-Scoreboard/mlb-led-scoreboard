from rgbmatrix import graphics
import ledcolors.scoreboard
import data.layout
import debug

NOHITTER_TEXT = "N.H"
PERFECT_GAME_TEXT = "P.G"
UNKNOWN_TEXT = "???"

class NoHitterRenderer:

  def __init__(self, canvas, data):
    self.canvas = canvas
    self.layout = data.config.layout

  def render(self):
    font = self.layout.font("nohitter")
    coords = self.layout.coords("nohitter")
    text_color = graphics.Color(*ledcolors.scoreboard.nohit)
    text = self.nohitter_text()
    graphics.DrawText(self.canvas, font["font"], coords["x"], coords["y"], text_color,  text)

  def nohitter_text(self):
  	if self.layout.state == data.layout.LAYOUT_STATE_NOHIT:
  		return NOHITTER_TEXT

  	if self.layout.state == data.layout.LAYOUT_STATE_PERFECT:
  		return PERFECT_GAME_TEXT

  	# If we get this far, the nohitter renderer probably shouldn't have been rendered.
  	debug.log("NoHitterRenderer is renderering with an unknown state.")
  	return UNKNOWN_TEXT
