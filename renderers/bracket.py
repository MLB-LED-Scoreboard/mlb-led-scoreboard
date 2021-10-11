try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from data.standings import League

from utils import get_standings_color_node


def __fill_bg(canvas, layout, colors, league):
    coords = layout.coords("standings")
    bg_color = get_standings_color_node(colors, "background", league)
    for y in range(0, coords["height"]):
        graphics.DrawLine(canvas, 0, y, coords["width"], y, bg_color)


def render_bracket(canvas, layout, colors, league: League):
    __fill_bg(canvas, layout, colors, league.name)

    coords = layout.coords("standings.postseason")
    font = layout.font("standings")
    team_name_color = get_standings_color_node(colors, "team.name", league.name)
    divider_color = get_standings_color_node(colors, "divider", league.name)

    matchup_gap = coords["matchup_y_gap"]
    winner_offset = matchup_gap // 2
    series_gap = coords["series_x_gap"]
    char_width = font["size"]["width"] + 2

    wc_x = coords["wc_x_start"]
    wc_y = coords["wc_y_start"]
    ds_x = wc_x + series_gap
    ds_a_y = wc_y + winner_offset
    ds_b_y = coords["ds_b_y_start"]
    lcs_x = ds_x + series_gap
    champ_y = (ds_b_y + ds_a_y) // 2 + winner_offset
    champ_x = lcs_x + series_gap

    # draw bracket lines
    # wc divider
    graphics.DrawLine(canvas, wc_x, wc_y, wc_x + series_gap - char_width // 2, wc_y, divider_color)
    # drop down
    graphics.DrawLine(canvas, ds_x - char_width // 2, wc_y, ds_x - char_width // 2, ds_a_y, divider_color)
    # ds a divider
    graphics.DrawLine(
        canvas, ds_x - char_width // 2, ds_a_y, ds_x + series_gap - char_width // 2, ds_a_y, divider_color
    )
    # connect to lcs
    graphics.DrawLine(
        canvas, lcs_x - char_width // 2, ds_a_y, lcs_x - char_width // 2, ds_a_y + winner_offset, divider_color
    )
    # ds b divider
    graphics.DrawLine(canvas, ds_x, ds_b_y, ds_x + series_gap - char_width // 2, ds_b_y, divider_color)
    # connect to lcs
    graphics.DrawLine(
        canvas, lcs_x - char_width // 2, ds_b_y, lcs_x - char_width // 2, ds_b_y - winner_offset, divider_color
    )
    # lcs horizonals
    graphics.DrawLine(
        canvas,
        lcs_x - char_width // 2,
        ds_a_y + winner_offset,
        lcs_x + series_gap - char_width // 2,
        ds_a_y + winner_offset,
        divider_color,
    )
    graphics.DrawLine(
        canvas,
        lcs_x - char_width // 2,
        ds_b_y - winner_offset,
        lcs_x + series_gap - char_width // 2,
        ds_b_y - winner_offset,
        divider_color,
    )
    # champ lines
    graphics.DrawLine(
        canvas,
        champ_x - char_width // 2,
        ds_a_y + winner_offset,
        champ_x - char_width // 2,
        ds_b_y - winner_offset,
        divider_color,
    )
    graphics.DrawLine(
        canvas, champ_x - char_width // 2, champ_y - winner_offset, champ_x, champ_y - winner_offset, divider_color,
    )

    # draw bracket text
    # wc teams
    graphics.DrawText(canvas, font["font"], wc_x, wc_y, team_name_color, league.wc2)
    graphics.DrawText(canvas, font["font"], wc_x, wc_y + matchup_gap, team_name_color, league.wc1)

    # DS A teams
    graphics.DrawText(canvas, font["font"], ds_x, ds_a_y, team_name_color, league.wc_winner)
    graphics.DrawText(canvas, font["font"], ds_x, ds_a_y + matchup_gap, team_name_color, league.ds_one)

    # DS B
    graphics.DrawText(canvas, font["font"], ds_x, ds_b_y, team_name_color, league.ds_three)
    graphics.DrawText(canvas, font["font"], ds_x, ds_b_y + matchup_gap, team_name_color, league.ds_two)

    # LCS
    graphics.DrawText(canvas, font["font"], lcs_x, ds_a_y + winner_offset, team_name_color, league.l_two)
    graphics.DrawText(canvas, font["font"], lcs_x, ds_b_y + winner_offset, team_name_color, league.l_one)

    # league champ
    graphics.DrawText(canvas, font["font"], champ_x + 1, champ_y, team_name_color, league.champ)

