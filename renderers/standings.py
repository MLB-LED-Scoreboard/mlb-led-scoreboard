from rgbmatrix import graphics
from utils import get_font
import ledcolors.standings
import time

def render(matrix, canvas, division):
  font = get_font()
  text_color = graphics.Color(*ledcolors.standings.text)

  canvas.Fill(*ledcolors.standings.fill)

  if canvas.width > 32:
    render_static_wide_standings(matrix, canvas, division, font, text_color)
  else:
    render_rotating_standings(matrix, canvas, division, font, text_color)

def render_rotating_standings(matrix, canvas, division, font, text_color):
  stat = 'w'
  starttime = time.time()
  while True:
    offset = 6
    graphics.DrawText(canvas, font, 28, offset, text_color, stat.upper())
    for team in division.teams:
      abbrev = '{:3s}'.format(team.team_abbrev)
      team_text = '%s' % abbrev
      stat_text = '%s' % getattr(team, stat)
      graphics.DrawText(canvas, font, 1 , offset, text_color, team_text)
      graphics.DrawText(canvas, font, 15, offset, text_color, stat_text)

      for x in range(0, canvas.width):
        canvas.SetPixel(x, offset, *ledcolors.standings.divider)
      for y in range(0, canvas.height):
        canvas.SetPixel(13, y, *ledcolors.standings.divider)
      offset += 6

    matrix.SwapOnVSync(canvas)
    time.sleep(5.0 - ((time.time() - starttime) % 5.0))

    canvas.Fill(*ledcolors.standings.fill)
    stat = 'w' if stat == 'l' else 'l'

def render_static_wide_standings(matrix, canvas, division, font, text_color):
  while True:
    offset = 6

    for team in division.teams:
      team_text = team.team_abbrev
      graphics.DrawText(canvas, font, 1, offset, text_color, team_text)

      team_record = str(team.w) + "-" + str(team.l)
      stat_text = '{:6s} {:4s}'.format(team_record, str(team.gb))
      stat_text_x = canvas.width - (len(stat_text) * 4)
      graphics.DrawText(canvas, font, stat_text_x, offset, text_color, stat_text)

      for x in range(0, canvas.width):
        canvas.SetPixel(x, offset, *ledcolors.standings.divider)
      for y in range(0, canvas.height):
        canvas.SetPixel(13, y, *ledcolors.standings.divider)
      offset += 6

      matrix.SwapOnVSync(canvas)

    time.sleep(20.0)
