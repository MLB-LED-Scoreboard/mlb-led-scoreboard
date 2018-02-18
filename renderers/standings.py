from rgbmatrix import graphics
from utils import get_font
import ledcolors.standings
import time

def render(matrix, canvas, division):
  font = get_font()
  text_color = graphics.Color(*ledcolors.standings.text)

  canvas.Fill(*ledcolors.standings.fill)

  stat = 'w'
  starttime = time.time()
  while True:
    offset = 6
    for team in division.teams:
      abbrev = '{:3s}'.format(team.team_abbrev)
      text = '%s %s' % (abbrev, getattr(team, stat))
      graphics.DrawText(canvas, font, 1, offset, text_color, text)

      for x in range(0, canvas.width):
        canvas.SetPixel(x, offset, *ledcolors.standings.divider)
      for y in range(0, canvas.height):
        canvas.SetPixel(14, y, *ledcolors.standings.divider)
      offset += 6

    matrix.SwapOnVSync(canvas)
    time.sleep(5.0 - ((time.time() - starttime) % 5.0))

    canvas.Fill(*ledcolors.standings.fill)
    stat = 'w' if stat == 'l' else 'l'
