try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from utils import center_text_position


def render_text(canvas, x, y, width, font, text_color, bg_color, text, scroll_pos):
    if __text_should_scroll(text, font, width):

        # this is done so that we don't need to draw a huge bar to the left of the text
        # used primarily in the 128x32 layout
        # see similar work done here https://github.com/ty-porter/RGBMatrixEmulator/pull/3
        w = font["size"]["width"]
        total_width = w * len(text)
        h = font["size"]["height"]

        # Offscreen to the left, adjust by first character width
        if scroll_pos - x < 0:
            adjustment = abs(scroll_pos - x + w) // w
            text = text[adjustment:]
            if adjustment:
                scroll_pos += w * adjustment

        if len(text) == 0:
            return 0

        graphics.DrawText(canvas, font["font"], scroll_pos, y, text_color, text)

        for xi in range(x - w * 2, x):
            graphics.DrawLine(canvas, xi, y + 1, xi, y + 1 - h, bg_color)
        for xi in range(x + width, canvas.width):
            graphics.DrawLine(canvas, xi, y + 1, xi, y + 1 - h, bg_color)

        return total_width

    else:
        graphics.DrawText(canvas, font["font"], __center_position(text, font, width, x), y, text_color, text)
        return 0


# Maybe the text is too short and we should just center it instead?
def __text_should_scroll(text, font, width):
    return len(text) * font["size"]["width"] > width


def __center_position(text, font, width, x):
    return center_text_position(text, abs(width // 2) + x, font["size"]["width"])


def __glyph_device_width(font, glyph):
    return font.bdf_font.glyph(glyph).meta["dwx0"]
