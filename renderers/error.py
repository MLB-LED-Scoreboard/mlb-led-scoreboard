try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from utils import center_text_position, get_font

""" Render a simple error message on the matrix

Properties:
  matrix                     - An instance of RGBMatrix
  canvas                     - The canvas associated with the matrix
  error_strings              - An array of up to 3 strings to be displayed
                               on the matrix. A 32 LED wide matrix can fit
                               8 characters per line.
"""


def render(matrix, canvas, error_strings):
    font = get_font()
    text_color = graphics.Color(255, 235, 59)
    current_y = 9
    offset = 7

    canvas.Fill(7, 14, 25)
    error_text = "ERROR"
    error_x = center_text_position(error_text, canvas.width // 2, 4)
    graphics.DrawText(canvas, font, error_x, 7, text_color, error_text)

    for error_string in error_strings:
        current_y += offset
        text = error_string
        text_x = center_text_position(text, canvas.width // 2, 4)
        graphics.DrawText(canvas, font, text_x, current_y, text_color, text)

    matrix.SwapOnVSync(canvas)
