from ledcoords import r32c32
import ledcolors.scoreboard

class OutsRenderer:
  def __init__(self, canvas, outs):
    self.canvas = canvas
    self.outs = outs

  def render(self):
    out_px = []
    out_px.append({'x': r32c32.OUT_1_X, 'y': r32c32.OUT_1_Y})
    out_px.append({'x': r32c32.OUT_2_X, 'y': r32c32.OUT_2_Y})
    out_px.append({'x': r32c32.OUT_3_X, 'y': r32c32.OUT_3_Y})
    for out in range(len(out_px)):
      self.__render_out_circle(out_px[out])
      # Fill in the circle if that out has occurred
      if (self.outs > out):
        self.canvas.SetPixel(out_px[out]['x'], out_px[out]['y'], *ledcolors.scoreboard.text)

  def __render_out_circle(self, out):
    offset = 1
    for x in range(-offset, offset + 1):
      for y in range(-offset, offset + 1):
        # The dead center is filled in only if that many outs has occurred, and happens above
        if x == 0 and y == 0:
          continue
        self.canvas.SetPixel(out['x'] + x, out['y'] + y, *ledcolors.scoreboard.text)
