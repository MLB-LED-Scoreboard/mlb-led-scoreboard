from driver import graphics
from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from renderers.games import nohitter
from bullpen.util import center_text_position, scrolling_text

NORMAL_GAME_LENGTH = 9


def render_postgame(
    canvas, layout: Layout, colors: Color, postgame: Postgame, scoreboard: Scoreboard, text_pos, is_playoffs
):
    _render_final_text(canvas, layout, colors, scoreboard)
    _render_recap_blurb(canvas, layout, colors, postgame.recap_blurb, text_pos)
    _render_divider(canvas, layout, colors)
    return _render_decision_rows(canvas, layout, colors, postgame, scoreboard, text_pos, is_playoffs)


def _render_recap_blurb(canvas, layout, colors, blurb, text_pos):
    if not blurb:
        return
    try:
        coords = layout.coords("final.recap_blurb")
    except KeyError:
        return
    font = layout.font("final.recap_blurb")
    color = colors.graphics_color("atbat.pitcher")
    bgcolor = colors.graphics_color("default.background")
    return scrolling_text(canvas, graphics, coords["x"], coords["y"], coords["width"],
                          font, color, bgcolor, blurb, text_pos)


def _render_divider(canvas, layout, colors):
    try:
        divider_y = layout.coords("teams.background.away")["y"] - 1
    except KeyError:
        divider_y = 27
    color = colors.graphics_color("atbat.pitcher")
    graphics.DrawLine(canvas, 0, divider_y, canvas.width - 1, divider_y, color)


def _render_final_text(canvas, layout, colors, scoreboard):
    text = "FINAL"
    if scoreboard.inning.number != NORMAL_GAME_LENGTH:
        text += "/" + str(scoreboard.inning.number)

    color = colors.graphics_color("final.inning")
    coords = layout.coords("final.inning")
    font = layout.font("final.inning")
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)

    if layout.state_is_nohitter():
        nohit_text = nohitter._get_nohitter_text(layout)
        nohit_coords = layout.coords("final.nohit_text")
        nohit_color = colors.graphics_color("final.nohit_text")
        nohit_font = layout.font("final.nohit_text")
        graphics.DrawText(canvas, nohit_font["font"], nohit_coords["x"], nohit_coords["y"], nohit_color, nohit_text)


def _render_decision_rows(canvas, layout, colors, postgame: Postgame, scoreboard: Scoreboard, text_pos, is_playoffs):
    """Show W/SV next to the winning team row, L next to the losing team row."""
    away_won = scoreboard.away_team.runs > scoreboard.home_team.runs

    winner_text = "W: {} ({}-{})".format(
        postgame.winning_pitcher,
        postgame.winning_pitcher_wins,
        postgame.winning_pitcher_losses,
    )
    if postgame.save_pitcher:
        winner_text += "  SV: {} ({})".format(postgame.save_pitcher, postgame.save_pitcher_saves)
    if is_playoffs:
        winner_text += "   " + postgame.series_status

    loser_text = "L: {} ({}-{})".format(
        postgame.losing_pitcher,
        postgame.losing_pitcher_wins,
        postgame.losing_pitcher_losses,
    )

    away_text = winner_text if away_won else loser_text
    home_text = loser_text if away_won else winner_text

    p1 = _render_row_pitcher(canvas, layout, colors, "away", away_text, text_pos)
    p2 = _render_row_pitcher(canvas, layout, colors, "home", home_text, text_pos)
    return max(p1, p2)


def _render_row_pitcher(canvas, layout, colors, side, text, text_pos):
    try:
        coords = layout.coords(f"final.{side}_pitcher")
    except KeyError:
        return 0
    font = layout.font(f"final.{side}_pitcher")
    color = colors.graphics_color("atbat.pitcher")
    bgcolor = colors.graphics_color("default.background")

    if len(text) * font["size"]["width"] <= coords["width"]:
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, text)
        return 0
    return scrolling_text(canvas, graphics, coords["x"], coords["y"], coords["width"],
                          font, color, bgcolor, text, text_pos)
