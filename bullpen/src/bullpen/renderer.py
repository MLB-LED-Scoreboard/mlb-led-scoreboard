import abc
from typing import TYPE_CHECKING, Any, Optional, Protocol


from .data import PluginData
from .config import Config, Layout, Color

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas
    from RGBMatrixEmulator import Color as GraphicsColor, Font


class graphics(Protocol):
    def DrawText(self, canvas: "Canvas", font: "Font", x: int, y: int, color: "GraphicsColor", text: str) -> int: ...

    def DrawLine(self, canvas: "Canvas", x1: int, y1: int, x2: int, y2: int, color: "GraphicsColor") -> None: ...

    def DrawCircle(self, canvas: "Canvas", x: int, y: int, r: int, color: "GraphicsColor") -> None: ...


class Renderer(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config: Config, layout: Layout, colors: Color) -> None: ...

    @abc.abstractmethod
    def wait_time(self) -> float: ...

    @abc.abstractmethod
    def render(
        self, data: PluginData, canvas: "Canvas", graphics: graphics, scrolling_text_pos: int
    ) -> Optional[int]: ...

    def reset(self):
        """Called at the end of rendering, can be used to reset state before switching off"""
        pass


def center_text_position(text: str, center_pos: int, font_width: int) -> int:
    return abs(center_pos - ((len(text) * font_width) // 2))


def scrolling_text(
    canvas: "Canvas",
    graphics: graphics,
    x: int,
    y: int,
    width: int,
    font: dict[str, Any],
    text_color: "GraphicsColor",
    bg_color: "GraphicsColor",
    text: str,
    scroll_pos: int,
    center: bool = True,
    force_scroll: bool = False,
) -> int:
    if force_scroll or __text_should_scroll(text, font, width):

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
            right = -((visible_width - width) // w)

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
