from rgbmatrix import graphics
from data.layout import Layout
import ledcolors.scoreboard
import data.layout

class BasesRenderer:
  """Renders the bases on the scoreboard and fills them in if they
  currently hold a runner."""

  def __init__(self, canvas, bases, data):
    self.canvas = canvas
    self.bases = bases
    self.layout = data.config.layout

  def render(self):
    base_runners = self.bases.runners
    color = graphics.Color(*ledcolors.scoreboard.text)

    base_px = []
    base_px.append(self.layout.coords("bases.1B"))
    base_px.append(self.layout.coords("bases.2B"))
    base_px.append(self.layout.coords("bases.3B"))

    for base in range(len(base_runners)):
      self.__render_base_outline(base_px[base], color)

      # Fill in the base if there's currently a baserunner
      if base_runners[base]:
        self.__render_baserunner(base_px[base], color)

  def __render_base_outline(self, base, color):
    x, y = (base["x"], base["y"])
    size = base["size"]
    half = abs(size/2)
    graphics.DrawLine(self.canvas, x + half, y, x, y + half, color)
    graphics.DrawLine(self.canvas, x + half, y, x + size, y + half, color)
    graphics.DrawLine(self.canvas, x + half, y + size, x, y + half, color)
    graphics.DrawLine(self.canvas, x + half, y + size, x + size, y + half, color)

  def __render_baserunner(self, base, color):
    x, y = (base["x"], base["y"])
    size = base["size"]
    half = abs(size/2)
    for offset in range(1, half+1):
      graphics.DrawLine(self.canvas, x + half - offset, y + size - offset, x + half + offset, y + size - offset, color)
      graphics.DrawLine(self.canvas, x + half - offset, y + offset, x + half + offset, y + offset, color)
