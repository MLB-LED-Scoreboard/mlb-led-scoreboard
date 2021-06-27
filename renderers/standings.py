try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from data.config.color import Color
from data.config.layout import Layout
from data.standings import Standings
from utils import center_text_position


def render_standings(canvas, layout: Layout, colors: Color, standings: Standings, stat):
    __fill_bg(canvas, layout, colors)
    if canvas.width > 32:
        __render_static_wide_standings(canvas, layout, colors, standings)
    else:
        return __render_rotating_standings(canvas, layout, colors, standings, stat)


def __fill_bg(canvas, layout, colors):
    coords = layout.coords("standings")
    bg_color = colors.graphics_color("standings.background")
    for y in range(0, coords["height"]):
        graphics.DrawLine(canvas, 0, y, coords["width"], y, bg_color)


def __render_rotating_standings(canvas, layout, colors, standings, stat):
    coords = layout.coords("standings")
    font = layout.font("standings")
    divider_color = colors.graphics_color("standings.divider")
    stat_color = colors.graphics_color("standings.stat")
    team_stat_color = colors.graphics_color("standings.team.stat")
    team_name_color = colors.graphics_color("standings.team.name")
    offset = coords["offset"]

    graphics.DrawLine(canvas, 0, 0, coords["width"], 0, divider_color)

    graphics.DrawText(canvas, font["font"], coords["stat_title"]["x"], offset, stat_color, stat.upper())
    graphics.DrawLine(canvas, coords["divider"]["x"], 0, coords["divider"]["x"], coords["height"], divider_color)

    for team in standings.current_standings().teams:
        graphics.DrawLine(canvas, 0, offset, coords["width"], offset, divider_color)

        team_text = "{:3s}".format(team.team_abbrev)
        stat_text = str(getattr(team, stat))
        graphics.DrawText(canvas, font["font"], coords["team"]["name"]["x"], offset, team_name_color, team_text)
        graphics.DrawText(canvas, font["font"], coords["team"]["record"]["x"], offset, team_stat_color, stat_text)

        offset += coords["offset"]


def __render_static_wide_standings(canvas, layout, colors, standings):
    coords = layout.coords("standings")
    font = layout.font("standings")
    divider_color = colors.graphics_color("standings.divider")
    team_stat_color = colors.graphics_color("standings.team.stat")
    team_name_color = colors.graphics_color("standings.team.name")
    offset = coords["offset"]

    graphics.DrawLine(canvas, 0, 0, coords["width"], 0, divider_color)

    graphics.DrawLine(canvas, coords["divider"]["x"], 0, coords["divider"]["x"], coords["height"], divider_color)

    for team in standings.current_standings().teams:
        graphics.DrawLine(canvas, 0, offset, coords["width"], offset, divider_color)

        team_text = team.team_abbrev
        graphics.DrawText(canvas, font["font"], coords["team"]["name"]["x"], offset, team_name_color, team_text)

        record_text = "{}-{}".format(team.w, team.l)
        record_text_x = center_text_position(record_text, coords["team"]["record"]["x"], font["size"]["width"])

        if "-" in str(team.gb):
            gb_text = " -  "
        else:
            gb_text = "{:>4s}".format(str(team.gb))
        gb_text_x = coords["team"]["games_back"]["x"] - (len(gb_text) * font["size"]["width"])

        graphics.DrawText(canvas, font["font"], record_text_x, offset, team_stat_color, record_text)
        graphics.DrawText(canvas, font["font"], gb_text_x, offset, team_stat_color, gb_text)

        offset += coords["offset"]

    __fill_standings_footer(canvas, layout, divider_color)


def __fill_standings_footer(canvas, layout, divider_color):
    coords = layout.coords("standings")
    graphics.DrawLine(canvas, 0, coords["height"], coords["width"], coords["height"], divider_color)

    graphics.DrawLine(canvas, 0, coords["height"] + 1, coords["width"], coords["height"] + 1, graphics.Color(0, 0, 0))
