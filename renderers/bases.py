from ledcoords import r32c32
import ledcolors.scoreboard

class BasesRenderer:
  def __init__(self, canvas, bases):
    self.canvas = canvas
    self.bases = bases

  def render(self):
    base_px = []
    base_px.append({'x': r32c32.FIRST_BASE_X, 'y': r32c32.FIRST_BASE_Y} )
    base_px.append({'x': r32c32.SECOND_BASE_X, 'y': r32c32.SECOND_BASE_Y} )
    base_px.append({'x': r32c32.THIRD_BASE_X, 'y': r32c32.THIRD_BASE_Y} )

    for base in range(len(self.bases)):
      self.__render_base_outline(base_px[base])

      # Fill in the base if there's currently a baserunner
      if self.bases[base]:
        self.__render_baserunner(base_px[base])

  def __render_base_outline(self, base):
    # Hollow diamonds are a popular homework problem but IDGAF
    self.canvas.SetPixel(base['x'] - 3, base['y'], *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 2, base['y'] - 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 2, base['y'] + 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 1, base['y'] - 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] - 1, base['y'] + 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'], base['y'] - 3, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'], base['y'] + 3, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 1, base['y'] - 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 1, base['y'] + 2, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 2, base['y'] - 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 2, base['y'] + 1, *ledcolors.scoreboard.text)
    self.canvas.SetPixel(base['x'] + 3, base['y'], *ledcolors.scoreboard.text)

  def __render_baserunner(self, base):
    offset = 2
    for x in range(-offset, offset + 1):
      for y in range(-offset, offset + 1):
        if abs(x) == offset and abs(y) == offset:
          continue
        self.canvas.SetPixel(base['x'] + x, base['y'] + y, *ledcolors.scoreboard.text)
