try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics


def render_team_banner(canvas, layout, team_colors, home_team, away_team, full_team_names):
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

    __render_team_text(canvas, layout, away_colors, away_team, "away", full_team_names, default_colors)
    __render_team_text(canvas, layout, home_colors, home_team, "home", full_team_names, default_colors)

    # Number of characters in each score.
    score_spacing = {
        "runs": max(len(str(away_team.runs)), len(str(home_team.runs))),
        "hits": max(len(str(away_team.hits)), len(str(home_team.hits))),
        "errors": max(len(str(away_team.errors)), len(str(home_team.errors))),
    }
    __render_team_score(canvas, layout, away_colors, away_team, "away", default_colors, score_spacing)
    __render_team_score(canvas, layout, home_colors, home_team, "home", default_colors, score_spacing)


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
    team_text = "{:3s}".format(team.abbrev.upper())
    if full_team_names and canvas.width > 32:
        team_text = "{:13s}".format(team.name)
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], text_color_graphic, team_text)


def __render_score_component(canvas, layout, colors, homeaway, default_colors, coords, component_val, width_chars):
    # The coords passed in are the rightmost pixel.
    font = layout.font(f"teams.runs.{homeaway}")
    font_width = font["size"]["width"]
    # Number of pixels between runs/hits and hits/errors.
    rhe_spacing = layout.coords(f"teams.runs.runs_hits_errors.spacing")
    text_color = colors.get("text", default_colors["text"])
    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    component_val = str(component_val)
    compress_digits = layout.coords(f"teams.runs.runs_hits_errors.compress_digits")
    # Draw each digit from right to left.
    for i, c in enumerate(component_val[::-1]):
        if i > 0 and compress_digits:
            coords["x"] += 1
        char_draw_x = coords["x"] - font_width * (i + 1)  # Determine character position
        graphics.DrawText(canvas, font["font"], char_draw_x, coords["y"], text_color_graphic, c)
    if compress_digits:
        coords["x"] += width_chars - len(component_val)  # adjust for compaction on values not rendered
    coords["x"] -= font_width * width_chars + rhe_spacing - 1  # adjust coordinates for next score.


def __render_team_score(canvas, layout, colors, team, homeaway, default_colors, score_spacing):
    coords = layout.coords(f"teams.runs.{homeaway}").copy()
    if layout.coords(f"teams.runs.runs_hits_errors.show"):
        __render_score_component(
            canvas, layout, colors, homeaway, default_colors, coords, team.errors, score_spacing["errors"]
        )
        __render_score_component(
            canvas, layout, colors, homeaway, default_colors, coords, team.hits, score_spacing["hits"]
        )
    __render_score_component(canvas, layout, colors, homeaway, default_colors, coords, team.runs, score_spacing["runs"])
