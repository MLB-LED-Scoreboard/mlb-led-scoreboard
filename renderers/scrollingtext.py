try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from utils import center_text_position


def render_text(canvas, x, y, width, font, text_color, bg_color, text, scroll_pos):
    if __text_should_scroll(text, font, width):
        pos = graphics.DrawText(canvas, font["font"], scroll_pos, y, text_color, text)
        h = font["size"]["height"]

        for xi in range(x):
            graphics.DrawLine(canvas, xi, y, xi, y - h, bg_color)
        for xi in range(x + width, canvas.width):
            graphics.DrawLine(canvas, xi, y, xi, y - h, bg_color)
        return pos

    else:
        graphics.DrawText(canvas, font["font"], __center_position(text, font, width, x), y, text_color, text)
        return 0


# Maybe the text is too short and we should just center it instead?
def __text_should_scroll(text, font, width):
    return len(text) * font["size"]["width"] > width


def __center_position(text, font, width, x):
    return center_text_position(text, abs(width // 2) + x, font["size"]["width"])
