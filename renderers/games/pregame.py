from driver import graphics
from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard.pregame import Pregame
from renderers import scrollingtext
from utils import center_text_position


def render_pregame(
    canvas, layout: Layout, colors: Color, pregame: Pregame, probable_starter_pos, pregame_weather, is_playoffs
):
    text_len = _render_pregame_info(canvas, layout, colors, pregame, probable_starter_pos, pregame_weather, is_playoffs)

    if layout.state_is_warmup():
        _render_warmup(canvas, layout, colors, pregame)
    else:
        _render_start_time(canvas, layout, colors, pregame)

    return text_len


def _render_start_time(canvas, layout, colors, pregame):
    time_text = pregame.start_time
    coords = layout.coords("pregame.start_time")
    font = layout.font("pregame.start_time")
    color = colors.graphics_color("pregame.start_time")
    time_x = center_text_position(time_text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], time_x, coords["y"], color, time_text)


def _render_warmup(canvas, layout, colors, pregame):
    warmup_text = pregame.status
    coords = layout.coords("pregame.warmup_text")
    font = layout.font("pregame.warmup_text")
    color = colors.graphics_color("pregame.warmup_text")
    warmup_x = center_text_position(warmup_text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], warmup_x, coords["y"], color, warmup_text)


def _render_pregame_info(canvas, layout, colors, pregame: Pregame, probable_starter_pos, pregame_weather, is_playoffs):
    coords = layout.coords("pregame.scrolling_text")
    font = layout.font("pregame.scrolling_text")
    color = colors.graphics_color("pregame.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    pitchers_text = pregame.away_starter + " vs " + pregame.home_starter
    if pregame.national_broadcasts:
        pitchers_text += " TV: " + ", ".join(pregame.national_broadcasts)
    if pregame_weather and pregame.pregame_weather:
        pitchers_text += " Weather: " + pregame.pregame_weather

    if is_playoffs:
        pitchers_text += "   " + pregame.series_status

    return scrollingtext.render_text(
        canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, pitchers_text, probable_starter_pos
    )
