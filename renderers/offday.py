from rgbmatrix import graphics
import ledcolors.scoreboard

def render(matrix, canvas):
  font = graphics.Font()
  font.LoadFont('Assets/tom-thumb.bdf')
  text_color = graphics.Color(*ledcolors.scoreboard.text)

  canvas.Fill(*ledcolors.scoreboard.fill)
  graphics.DrawText(canvas, font, 12, 8, text_color, 'No')
  graphics.DrawText(canvas, font, 6, 15, text_color, 'games')
  graphics.DrawText(canvas, font, 6, 22, text_color, 'today')
  graphics.DrawText(canvas, font, 12, 29, text_color, ':(')
  matrix.SwapOnVSync(canvas)

  while True:
    pass # I hate the offseason and off days.
