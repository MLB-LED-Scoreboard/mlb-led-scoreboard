from driver import graphics
from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard.pregame import Pregame

from bullpen.util import center_text_position, scrolling_text


def render_pregame(
    canvas, layout: Layout, colors: Color, pregame: Pregame, text_pos, pregame_weather, is_playoffs
):
    # Top row: start time (or Warmup) centered
    if layout.state_is_warmup():
        _render_warmup(canvas, layout, colors, pregame)
    else:
        _render_start_time(canvas, layout, colors, pregame)

    # Second row: weather scrolling full width
    if pregame_weather and pregame.pregame_weather:
        _render_weather_scroll(canvas, layout, colors, pregame, text_pos)

    _render_divider(canvas, layout, colors)

    # Team rows: pitcher next to each team (scrolling if needed)
    p1 = _render_team_pitcher(canvas, layout, colors, "away", pregame.away_starter, text_pos)
    p2 = _render_team_pitcher(canvas, layout, colors, "home", pregame.home_starter, text_pos)

    if is_playoffs:
        pass  # series status could go in top row in a future iteration

    return max(p1, p2)


def _render_divider(canvas, layout, colors):
    try:
        divider_y = layout.coords("teams.background.away")["y"] - 1
    except KeyError:
        divider_y = 27
    color = colors.graphics_color("atbat.pitcher")
    graphics.DrawLine(canvas, 0, divider_y, canvas.width - 1, divider_y, color)


def _render_start_time(canvas, layout, colors, pregame):
    text = pregame.start_time
    coords = layout.coords("pregame.start_time")
    font = layout.font("pregame.start_time")
    color = colors.graphics_color("pregame.start_time")
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)


def _render_warmup(canvas, layout, colors, pregame):
    text = pregame.status
    coords = layout.coords("pregame.warmup_text")
    font = layout.font("pregame.warmup_text")
    color = colors.graphics_color("pregame.warmup_text")
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)


def _render_weather_scroll(canvas, layout, colors, pregame: Pregame, text_pos):
    try:
        coords = layout.coords("pregame.weather_scroll")
    except KeyError:
        return
    font = layout.font("pregame.weather_scroll")
    color = colors.graphics_color("pregame.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    text = pregame.pregame_weather or ""
    if not text:
        return
    text_px = len(text) * font["size"]["width"]
    if text_px <= coords["width"]:
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, text)
    else:
        scrolling_text(canvas, graphics, coords["x"], coords["y"], coords["width"],
                       font, color, bgcolor, text, text_pos)


def _render_team_pitcher(canvas, layout, colors, side, pitcher_text, text_pos):
    try:
        coords = layout.coords(f"pregame.{side}_pitcher")
    except KeyError:
        return 0
    font = layout.font(f"pregame.{side}_pitcher")
    color = colors.graphics_color("atbat.pitcher")
    bgcolor = colors.graphics_color("default.background")

    if len(pitcher_text) * font["size"]["width"] <= coords["width"]:
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, pitcher_text)
        return 0
    return scrolling_text(canvas, graphics, coords["x"], coords["y"], coords["width"],
                          font, color, bgcolor, pitcher_text, text_pos)
