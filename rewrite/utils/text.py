from driver import graphics

from dataclasses import dataclass


@dataclass
class TextPosition:
    x: int = 0
    y: int = 0


class ScrollingText:
    def __init__(self, canvas, x, y, width, start_x, font, font_size, text_color, bg_color, text, center=True):
        # Matrix
        self.canvas = canvas

        # Start X and Y
        self.end_position = TextPosition(x=x, y=y)

        # Font options
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color

        # Text
        self.text = text
        self._centered_text = None

        # Scroll options
        self.width = width
        self.center = center

        # Current position
        self.position = TextPosition(x=start_x, y=y)
        self.finished = False

    def __should_scroll(self):
        return len(self.text) * self.font_size[0] > self.width

    def render_text(self):
        if self.finished:
            return

        if self.__should_scroll():
            self.__render_scroll_text()
        else:
            self.__render_static_text(self.center)
            self.finished = True

    def __render_scroll_text(self):
        # This is done so that we don't need to draw a huge bar to the left of the text.
        # Used primarily in the 128x32 layout.
        # See similar work done here https://github.com/ty-porter/RGBMatrixEmulator/pull/3
        font_w, font_h = self.font_size
        total_width = font_w * len(self.text)

        text, offset = self.__truncate_text(self.text, *self.font_size)

        if len(text) == 0:
            self.finished = True

            return

        for y_offset in range(0, font_h):
            graphics.DrawLine(
                self.canvas,
                min(0, self.end_position.x - font_w),
                self.end_position.y + 1 - font_h + y_offset,
                min(self.width, self.canvas.width),
                self.end_position.y + 1 - font_h + y_offset,
                self.bg_color,
            )

        graphics.DrawText(self.canvas, self.font, self.position.x + offset, self.position.y, self.text_color, text)

        self.__perform_scroll(total_width)

    def __render_static_text(self, center):
        if center:
            if self._centered_text is None:
                self._centered_text = CenteredText(
                    self.canvas,
                    self.position.x,
                    self.position.y,
                    self.font,
                    self.font_size,
                    self.text_color,
                    self.text,
                    bg_color=None,
                )

            self._centered_text.render_text()
        else:
            graphics.DrawText(self.canvas, self.font, self.position.x, self.position.y, self.text_color, self.text)

    def __truncate_text(self, text, font_w, font_h):
        text = self.text

        # Offscreen to the left, adjust by first character width
        if self.position.x - self.end_position.x < 0:
            adjustment = abs(self.position.x - self.end_position.x) // font_w
            text = text[adjustment:]

            return (text, adjustment * font_w)

        return (text, 0)

    def __perform_scroll(self, text_width):
        next_x = self.position.x - 1

        if text_width + next_x < 0:
            self.finished = True

            return

        self.position.x = next_x


class CenteredText:
    def __init__(self, canvas, x, y, font, font_size, text_color, text, bg_color=None):
        # Matrix
        self.canvas = canvas

        # Font options
        self.font = font
        self.font_size = font_size
        self.text_color = text_color
        self.bg_color = bg_color

        # Text
        self.text = text

        # Current position
        self._position = TextPosition(x=x, y=y)
        self.position = TextPosition(x=self.__calculate_center(), y=y)

    def render_text(self):
        # TODO: Add background optional
        graphics.DrawText(self.canvas, self.font, self.position.x, self.position.y, self.text_color, self.text)

    def __calculate_center(self):
        return abs(self._position.x - ((len(self.text) * self.font_size[0]) // 2))
