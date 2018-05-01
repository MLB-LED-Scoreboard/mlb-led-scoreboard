from rgbmatrix import graphics
import ledcolors.scoreboard

class OutsRenderer:
  """Renders the out circles on the scoreboard."""

  def __init__(self, canvas, outs, coords):
    self.canvas = canvas
    self.outs = outs
    self.coords = coords

  def render(self):
    out_px = []
    out_px.append(self.coords[0])
    out_px.append(self.coords[1])
    out_px.append(self.coords[2])
    color = graphics.Color(*ledcolors.scoreboard.text)
    
    for out in range(len(out_px)):
      self.__render_out_circle(out_px[out], color)
      # Fill in the circle if that out has occurred
      if (self.outs.number > out):
        self.__fill_circle(out_px[out], color)

  def __render_out_circle(self, out, color):
    x, y, size = (out["x"], out["y"], out["size"])
    graphics.DrawLine(self.canvas, x, y, x + size, y, color)
    graphics.DrawLine(self.canvas, x, y, x, y + size, color)
    graphics.DrawLine(self.canvas, x + size, y + size, x, y + size, color)
    graphics.DrawLine(self.canvas, x + size, y + size, x + size, y, color)

  def __fill_circle(self, out, color):
    size = out["size"]
    x, y = (out["x"], out["y"])
    for y_offset in range(size):
      graphics.DrawLine(self.canvas, x, y + y_offset, x + size, y + y_offset, color)
