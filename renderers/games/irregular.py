try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from data import status
from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard import Scoreboard
from renderers import scrollingtext
from utils import center_text_position

# "Manager Challenge is too long"
CHALLENGE_SHORTHAND = "Challenge"

# Handle statuses that are too long for 32-wide boards.
POSTPONED_SHORTHAND = "Postpd"
CANCELLED_SHORTHAND = "Cancl'd"
SUSPENDED_SHORTHAND = "Suspnd"
CHALLENGE_SHORTHAND_32 = "Chalnge"
UMPIRE_REVIEW_SHORTHAND = "Review"


def render_irregular_status(canvas, layout: Layout, colors: Color, scoreboard: Scoreboard, short_text, text_pos=0):
    pos = 0
    if scoreboard.get_text_for_reason():
        pos = __render_scroll_text(canvas, layout, colors, scoreboard, text_pos)

    __render_game_status(canvas, layout, colors, scoreboard, short_text)

    return pos


def __render_game_status(canvas, layout, colors, scoreboard, short_text):
    color = colors.graphics_color("status.text")
    text = __get_text_for_status(scoreboard, short_text)
    coords = layout.coords("status.text")
    font = layout.font("status.text")
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)


def __render_scroll_text(canvas, layout, colors, scoreboard, text_pos):
    coords = layout.coords("status.scrolling_text")
    font = layout.font("status.scrolling_text")
    color = colors.graphics_color("status.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    scroll_text = scoreboard.get_text_for_reason()
    return scrollingtext.render_text(
        canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, scroll_text, text_pos
    )


def __get_text_for_status(scoreboard, short_text):
    text = scoreboard.game_status
    if ":" in text:
        text = text.split(":")[0]
    if short_text:
        return __get_short_text(text)
    if "challenge" in text:
        return CHALLENGE_SHORTHAND
    if "review" in text:
        return UMPIRE_REVIEW_SHORTHAND

    if text == status.DELAYED_START:
        return status.DELAYED

    return text


def __get_short_text(text):
    if "delayed" in text.lower():
        return status.DELAYED
    if "postponed" in text.lower():
        return POSTPONED_SHORTHAND
    if "cancelled" in text.lower():
        return CANCELLED_SHORTHAND
    if "challenge" in text.lower():
        return CHALLENGE_SHORTHAND_32
    if "review" in text.lower():
        return UMPIRE_REVIEW_SHORTHAND
    if "suspended" in text.lower():
        return SUSPENDED_SHORTHAND
    return text
