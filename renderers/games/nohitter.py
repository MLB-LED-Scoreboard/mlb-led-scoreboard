try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

import data.config.layout as cfglayout
import debug

NOHITTER_TEXT = "N.H"
PERFECT_GAME_TEXT = "P.G"
UNKNOWN_TEXT = "???"


def render_nohit_text(canvas, layout, colors):
    font = layout.font("nohitter")
    coords = layout.coords("nohitter")
    text_color = colors.graphics_color("nohit_text")
    text = _get_nohitter_text(layout)
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], text_color, text)


def _get_nohitter_text(layout):
    if layout.state == cfglayout.LAYOUT_STATE_NOHIT:
        return NOHITTER_TEXT

    if layout.state == cfglayout.LAYOUT_STATE_PERFECT:
        return PERFECT_GAME_TEXT

    # If we get this far, the nohitter renderer probably shouldn't have been rendered.
    debug.log("No Hitter text is renderering with an unknown state.")
    return UNKNOWN_TEXT
