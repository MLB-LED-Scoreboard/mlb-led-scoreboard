from driver import graphics

ABSOLUTE = "absolute"
RELATIVE = "relative"

def render_team_banner(
    canvas, layout, team_colors, home_team, away_team, full_team_names, short_team_names_for_runs_hits, show_score,
):
    default_colors = team_colors.color("default")

    away_colors = __team_colors(team_colors, away_team.abbrev)
    try:
        away_team_color = away_colors["home"]
    except KeyError:
        away_team_color = team_colors.color("default.home")

    home_colors = __team_colors(team_colors, home_team.abbrev)
    try:
        home_team_color = home_colors["home"]
    except KeyError:
        home_team_color = team_colors.color("default.home")

    try:
        away_team_accent = away_colors["accent"]
    except KeyError:
        away_team_accent = team_colors.color("default.accent")

    try:
        home_team_accent = home_colors["accent"]
    except KeyError:
        home_team_accent = team_colors.color("default.accent")

    bg_coords = {}
    bg_coords["away"] = layout.coords("teams.background.away")
    bg_coords["home"] = layout.coords("teams.background.home")

    accent_coords = {}
    accent_coords["away"] = layout.coords("teams.accent.away")
    accent_coords["home"] = layout.coords("teams.accent.home")

    for team in ["away", "home"]:
        for x in range(bg_coords[team]["width"]):
            for y in range(bg_coords[team]["height"]):
                color = away_team_color if team == "away" else home_team_color
                x_offset = bg_coords[team]["x"]
                y_offset = bg_coords[team]["y"]
                canvas.SetPixel(x + x_offset, y + y_offset, color["r"], color["g"], color["b"])

    for team in ["away", "home"]:
        for x in range(accent_coords[team]["width"]):
            for y in range(accent_coords[team]["height"]):
                color = away_team_accent if team == "away" else home_team_accent
                x_offset = accent_coords[team]["x"]
                y_offset = accent_coords[team]["y"]
                canvas.SetPixel(x + x_offset, y + y_offset, color["r"], color["g"], color["b"])

    use_full_team_names = can_use_full_team_names(
        canvas, full_team_names, short_team_names_for_runs_hits, [home_team, away_team]
    )

    away_name_end_pos = __render_team_text(canvas, layout, away_colors, away_team, "away", use_full_team_names, default_colors)
    home_name_end_pos = __render_team_text(canvas, layout, home_colors, home_team, "home", use_full_team_names, default_colors)

    __render_record_text(canvas, layout, away_colors, away_team, "away", default_colors, away_name_end_pos)
    __render_record_text(canvas, layout, home_colors, home_team, "home", default_colors, home_name_end_pos)

    if show_score:
        # Number of characters in each score.
        score_spacing = {
            "runs": max(len(str(away_team.runs)), len(str(home_team.runs))),
            "hits": max(len(str(away_team.hits)), len(str(home_team.hits))),
            "errors": max(len(str(away_team.errors)), len(str(home_team.errors))),
        }
        __render_team_score(canvas, layout, away_colors, away_team, "away", default_colors, score_spacing)
        __render_team_score(canvas, layout, home_colors, home_team, "home", default_colors, score_spacing)


def can_use_full_team_names(canvas, enabled, abbreviate_on_overflow, teams):
    # Settings enabled and size is able to display it
    if enabled and canvas.width > 32:

        # If config enabled for abbreviating if runs or hits takes up an additional column (i.e. 9 -> 10)
        if abbreviate_on_overflow:

            # Iterate through the teams to see if we should abbreviate
            for team in teams:
                if team.runs > 9 or team.hits > 9:
                    return False

            # Else use full names if no stats column has overflowed
            return True

        # If config for abbreviating is not set, use full name
        else:
            return True

    # Fallback to abbreviated names for all cases
    return False


def __team_colors(team_colors, team_abbrev):
    try:
        team_colors = team_colors.color(team_abbrev.lower())
    except KeyError:
        team_colors = team_colors.color("default")
    return team_colors


def __render_team_text(canvas, layout, colors, team, homeaway, full_team_names, default_colors):
    text_color = colors.get("text", default_colors["text"])
    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    coords = layout.coords("teams.name.{}".format(homeaway))
    font = layout.font("teams.name.{}".format(homeaway))
    team_text = "{:3s}".format(team.abbrev.upper()).strip()
    if full_team_names:
        team_text = "{:13s}".format(team.name).strip()
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], text_color_graphic, team_text)

    return (coords["x"] + (len(team_text) * font["size"]["width"]), coords["y"])

def __render_record_text(canvas, layout, colors, team, homeaway, default_colors, origin):
    if "losses" not in team.record or "wins" not in team.record:
        return
    if not layout.coords("teams.record").get("enabled", False):
        return

    text_color = colors.get("text", default_colors["text"])
    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    coords = layout.coords("teams.record.{}".format(homeaway))
    font = layout.font("teams.record.{}".format(homeaway))
    record_text = "({}-{})".format(team.record["wins"], team.record["losses"])

    if layout.coords("teams.record").get("position", ABSOLUTE) != RELATIVE:
        origin = (0, 0)

    x = coords["x"] + origin[0]
    y = coords["y"] + origin[1]

    graphics.DrawText(canvas, font["font"], x, y, text_color_graphic, record_text)

def __render_score_component(canvas, layout, colors, homeaway, default_colors, coords, component_val, width_chars):
    # The coords passed in are the rightmost pixel.
    font = layout.font(f"teams.runs.{homeaway}")
    font_width = font["size"]["width"]
    # Number of pixels between runs/hits and hits/errors.
    rhe_coords = layout.coords("teams.runs.runs_hits_errors")
    text_color = colors.get("text", default_colors["text"])
    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    component_val = str(component_val)
    # Draw each digit from right to left.
    for i, c in enumerate(component_val[::-1]):
        if i > 0 and rhe_coords["compress_digits"]:
            coords["x"] += 1
        char_draw_x = coords["x"] - font_width * (i + 1)  # Determine character position
        graphics.DrawText(canvas, font["font"], char_draw_x, coords["y"], text_color_graphic, c)
    if rhe_coords["compress_digits"]:
        coords["x"] += width_chars - len(component_val)  # adjust for compaction on values not rendered
    coords["x"] -= font_width * width_chars + rhe_coords["spacing"] - 1  # adjust coordinates for next score.


def __render_team_score(canvas, layout, colors, team, homeaway, default_colors, score_spacing):
    coords = layout.coords(f"teams.runs.{homeaway}").copy()
    if layout.coords("teams.runs.runs_hits_errors")["show"]:
        __render_score_component(
            canvas, layout, colors, homeaway, default_colors, coords, team.errors, score_spacing["errors"]
        )
        __render_score_component(
            canvas, layout, colors, homeaway, default_colors, coords, team.hits, score_spacing["hits"]
        )
    __render_score_component(canvas, layout, colors, homeaway, default_colors, coords, team.runs, score_spacing["runs"])
