from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard

def render(matrix, canvas):
  font = get_font()
  text_color = graphics.Color(*ledcolors.scoreboard.text)

  canvas.Fill(*ledcolors.scoreboard.fill)
  no_text = 'No'
  no_x = center_text_position(no_text, canvas.width)
  graphics.DrawText(canvas, font, no_x, 8, text_color, no_text)

  games_text = 'games'
  games_x = center_text_position(games_text, canvas.width)
  graphics.DrawText(canvas, font, games_x, 15, text_color, games_text)

  today_text = 'today'
  today_x = center_text_position(today_text, canvas.width)
  graphics.DrawText(canvas, font, today_x, 22, text_color, today_text)

  frown_text = ':('
  frown_x = center_text_position(frown_text, canvas.width)
  graphics.DrawText(canvas, font, frown_x, 29, text_color, frown_text)
  
  matrix.SwapOnVSync(canvas)

  while True:
    pass # I hate the offseason and off days.
