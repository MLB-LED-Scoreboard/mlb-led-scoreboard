try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from renderers import scrollingtext
from renderers.games import nohitter
from utils import center_text_position

NORMAL_GAME_LENGTH = 9


def render_postgame(canvas, layout: Layout, colors: Color, postgame: Postgame, scoreboard: Scoreboard, text_pos):
    _render_final_inning(canvas, layout, colors, scoreboard)
    return _render_decision_scroll(canvas, layout, colors, postgame, text_pos)


def _render_decision_scroll(canvas, layout, colors, postgame, text_pos):
    coords = layout.coords("final.scrolling_text")
    font = layout.font("final.scrolling_text")
    color = colors.graphics_color("final.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    scroll_text = "W: {} {}-{} L: {} {}-{}".format(
        postgame.winning_pitcher,
        postgame.winning_pitcher_wins,
        postgame.winning_pitcher_losses,
        postgame.losing_pitcher,
        postgame.losing_pitcher_wins,
        postgame.losing_pitcher_losses,
    )
    if postgame.save_pitcher:
        scroll_text += " SV: {} ({})".format(postgame.save_pitcher, postgame.save_pitcher_saves)
    return scrollingtext.render_text(
        canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, scroll_text, text_pos
    )


def _render_final_inning(canvas, layout, colors, scoreboard):
    text = "FINAL"
    color = colors.graphics_color("final.inning")
    coords = layout.coords("final.inning")
    font = layout.font("final.inning")
    if scoreboard.inning.number != NORMAL_GAME_LENGTH:
        text += " " + str(scoreboard.inning.number)
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)

    if layout.state_is_nohitter():
        nohit_text = nohitter._get_nohitter_text(layout)
        nohit_coords = layout.coords("final.nohit_text")
        nohit_color = colors.graphics_color("final.nohit_text")
        nohit_font = layout.font("final.nohit_text")
        graphics.DrawText(canvas, nohit_font["font"], nohit_coords["x"], nohit_coords["y"], nohit_color, nohit_text)
