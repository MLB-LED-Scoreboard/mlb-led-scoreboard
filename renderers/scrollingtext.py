from driver import graphics

from utils import center_text_position


def render_text(canvas, x, y, width, font, text_color, bg_color, text, scroll_pos, center=True):
    if __text_should_scroll(text, font, width):

        w = font["size"]["width"]
        total_width = w * len(text)

        # if the text is long enough to scroll, we can trim it to only the visible
        # part plus one letter on either side to minimize drawing
        left = None
        right = None

        empty_space_at_start = scroll_pos - x

        # Offscreen to the left
        if empty_space_at_start < 0:
            left = abs(empty_space_at_start) // w

        # Offscreen to the right
        visible_width = total_width + empty_space_at_start
        if visible_width > width + w:
            right =  -((visible_width - width) // w)

        # Trim the text to only the visible part
        text = text[left:right]

        if len(text) == 0:
            return 0

        # if we trimmed to the left, we need to adjust the scroll position accordingly
        if left:
            scroll_pos += w * left

        graphics.DrawText(canvas, font["font"], scroll_pos, y, text_color, text)

        # draw one-letter boxes to left and right to hide previous and next letters
        top = y + 1
        bottom = top - font["size"]["height"]
        for xi in range(0, w):
            left = x - xi - 1
            graphics.DrawLine(canvas, left, top, left, bottom, bg_color)
            right = x + width + xi
            graphics.DrawLine(canvas, right, top, right, bottom, bg_color)

        return total_width
    else:
        draw_x = __center_position(text, font, width, x) if center else x
        graphics.DrawText(canvas, font["font"], draw_x, y, text_color, text)
        return 0


# Maybe the text is too short and we should just center it instead?
def __text_should_scroll(text, font, width):
    return len(text) * font["size"]["width"] > width


def __center_position(text, font, width, x):
    return center_text_position(text, abs(width // 2) + x, font["size"]["width"])
