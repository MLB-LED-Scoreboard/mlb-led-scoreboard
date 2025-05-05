from driver import graphics

ABSOLUTE = "absolute"
RELATIVE = "relative"

def render_team_banner(
    canvas, layout, team_colors, home_team, away_team, show_score,
):
    away_colors = away_team.lookup_color(team_colors)
    home_colors = home_team.lookup_color(team_colors)

    bg_coords = {}
    bg_coords["away"] = layout.coords("teams.background.away")
    bg_coords["home"] = layout.coords("teams.background.home")

    accent_coords = {}
    accent_coords["away"] = layout.coords("teams.accent.away")
    accent_coords["home"] = layout.coords("teams.accent.home")

    for team in ["away", "home"]:
        # Background
        bg_color = home_colors['home'] if team == "home" else away_colors['home']
        __draw_filled_box(canvas, bg_coords[team], bg_color)

        # Accent
        accent_color = home_colors['accent'] if team == "home" else away_colors['accent']
        __draw_filled_box(canvas, accent_coords[team], accent_color)

    use_full_team_names = can_use_full_team_names(layout, [home_team, away_team])

    away_name_end_pos = __render_team_text(canvas, layout, away_colors['text'], away_team, "away", use_full_team_names)
    home_name_end_pos = __render_team_text(canvas, layout, home_colors['text'], home_team, "home", use_full_team_names)

    __render_record_text(canvas, layout, away_colors['text'], away_team, "away", away_name_end_pos)
    __render_record_text(canvas, layout, home_colors['text'], home_team, "home", home_name_end_pos)

    if show_score:
        # Number of characters in each score.
        score_spacing = {
            "runs": max(len(str(away_team.runs)), len(str(home_team.runs))),
            "hits": max(len(str(away_team.hits)), len(str(home_team.hits))),
            "errors": max(len(str(away_team.errors)), len(str(home_team.errors))),
        }
        __render_team_score(canvas, layout, away_colors['text'], away_team, "away", score_spacing)
        __render_team_score(canvas, layout, home_colors['text'], home_team, "home", score_spacing)


def can_use_full_team_names(layout, teams):
    name_coords = layout.coords("teams.name")

    # Global setting is disabled
    if not name_coords.get("full", False):
        return False

    # Setting for abbreviating if a line score contains more than 3 total digits (i.e. R, H, or E >= 10)
    if name_coords.get("shorten_on_high_line_score", False):

        # For each team, check digits for each line score item. Disable full names if any exceed a single digit.
        # A 10 error game would be rough, but the edge case is covered...
        for team in teams:
            if team.runs > 9 or team.hits > 9 or team.errors > 9:
                return False

        # No line score column has overflowed
        return True

    # Global setting is enabled
    return True


def __render_team_text(canvas, layout, text_color, team, homeaway, full_team_names):
    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    coords = layout.coords("teams.name.{}".format(homeaway))
    font = layout.font("teams.name.{}".format(homeaway))
    team_text = "{:3s}".format(team.abbrev.upper()).strip()
    if full_team_names:
        team_text = "{:13s}".format(team.name).strip()
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], text_color_graphic, team_text)

    return (coords["x"] + (len(team_text) * font["size"]["width"]), coords["y"])

def __render_record_text(canvas, layout, text_color, team, homeaway, origin):
    if "losses" not in team.record or "wins" not in team.record:
        return
    if not layout.coords("teams.record").get("enabled", False):
        return

    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    coords = layout.coords("teams.record.{}".format(homeaway))
    font = layout.font("teams.record.{}".format(homeaway))
    record_text = "({}-{})".format(team.record["wins"], team.record["losses"])

    if layout.coords("teams.record").get("position", ABSOLUTE) != RELATIVE:
        origin = (0, 0)

    x = coords["x"] + origin[0]
    y = coords["y"] + origin[1]

    graphics.DrawText(canvas, font["font"], x, y, text_color_graphic, record_text)

def __render_score_component(canvas, layout, text_color, homeaway, coords, component_val, width_chars):
    # The coords passed in are the rightmost pixel.
    font = layout.font(f"teams.line_score.{homeaway}")
    font_width = font["size"]["width"]
    # Number of pixels between runs/hits and hits/errors.
    line_score_coords = layout.coords("teams.line_score")
    text_color_graphic = graphics.Color(text_color["r"], text_color["g"], text_color["b"])
    component_val = str(component_val)
    # Draw each digit from right to left.
    for i, c in enumerate(component_val[::-1]):
        if i > 0 and line_score_coords["compress_digits"]:
            coords["x"] += 1
        char_draw_x = coords["x"] - font_width * (i + 1)  # Determine character position
        graphics.DrawText(canvas, font["font"], char_draw_x, coords["y"], text_color_graphic, c)
    if line_score_coords["compress_digits"]:
        coords["x"] += width_chars - len(component_val)  # adjust for compaction on values not rendered
    coords["x"] -= font_width * width_chars + line_score_coords["spacing"] - 1  # adjust coordinates for next score.


def __render_team_score(canvas, layout, text_color, team, homeaway, score_spacing):
    coords = layout.coords(f"teams.line_score.{homeaway}").copy()
    if layout.coords("teams.line_score")["show_hits_and_errors"]:
        __render_score_component(
            canvas, layout, text_color, homeaway, coords, team.errors, score_spacing["errors"]
        )
        __render_score_component(
            canvas, layout, text_color, homeaway, coords, team.hits, score_spacing["hits"]
        )
    __render_score_component(canvas, layout, text_color, homeaway, coords, team.runs, score_spacing["runs"])

def __draw_filled_box(canvas, coords, color):
        c = graphics.Color(color["r"], color["g"], color["b"])

        x = coords["x"]
        y = coords["y"]
        w = coords["width"]

        for h in range(coords["height"]):
            graphics.DrawLine(canvas, x, y + h, x + w, y + h, c)
