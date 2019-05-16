from rgbmatrix import graphics
from utils import center_text_position
import data.layout
import debug

NETWORK_ERROR_TEXT = "!"

class NetworkErrorRenderer:
  def __init__(self, canvas, data):
    self.canvas = canvas
    self.data   = data
    self.layout = data.config.layout
    self.colors = data.config.scoreboard_colors

  def render(self):
    if self.data.network_issues == True:
      font = self.layout.font("network")
      coords = self.layout.coords("network")
      bg_coords = coords["background"]
      text_color = self.colors.graphics_color("network.text")
      bg_color = self.colors.color("network.background")

      # Fill in the background so it's clearly visible
      for x in range(bg_coords["width"]):
        for y in range(bg_coords["height"]):
          self.canvas.SetPixel(x + bg_coords["x"], y + bg_coords["y"], bg_color['r'], bg_color['g'], bg_color['b'])
      text = NETWORK_ERROR_TEXT
      x = center_text_position(text, coords["text"]["x"], font["size"]["width"]) 
      graphics.DrawText(self.canvas, font["font"], x, coords["text"]["y"], text_color, text)
