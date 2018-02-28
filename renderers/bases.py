import ledcolors.scoreboard

class BasesRenderer:
  """Renders the bases on the scoreboard and fills them in if they
  currently hold a runner."""

  def __init__(self, canvas, bases):
    self.canvas = canvas
    self.bases = bases

  def render(self):
    base_runners = self.bases.runners

    # Offset the bases if we have a wider screen
    # Adding 2 extra pixels to give it a little more space from the outs/count
    offset = 0
    if self.canvas.width > 32:
      offset = ((self.canvas.width - 32)/2) + 2

    base_px = []
    base_px.append({'x': 26 + offset, 'y': 27} )
    base_px.append({'x': 21 + offset, 'y': 22} )
    base_px.append({'x': 16 + offset, 'y': 27} )

    for base in range(len(base_runners)):
      self.__render_base_outline(base_px[base])

      # Fill in the base if there's currently a baserunner
      if base_runners[base]:
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