import time

from data import status
from driver import graphics
from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard import Scoreboard
from data.scoreboard.atbat import AtBat
from data.scoreboard.bases import Bases
from data.scoreboard.inning import Inning
from data.scoreboard.pitches import Pitches

from bullpen.util import scrolling_text
from renderers.games import nohitter

_play_desc_pos = None
_play_desc_last = None


def render_live_game(canvas, layout: Layout, colors: Color, scoreboard: Scoreboard, text_pos, animation_time):
    pos = 0
    if not status.is_inning_break(scoreboard.inning.state):
        pos = _render_batter_row(canvas, layout, colors, scoreboard.atbat, text_pos)
        _render_pitcher_row(canvas, layout, colors, scoreboard.atbat, scoreboard.pitches)
        _render_divider(canvas, layout, colors)

        should_display_nohitter = layout.coords("nohitter")["innings_until_display"]
        if scoreboard.inning.number > should_display_nohitter and layout.state_is_nohitter():
            nohitter.render_nohit_text(canvas, layout, colors)

        _render_count(canvas, layout, colors, scoreboard.pitches)
        _render_outs(canvas, layout, colors, scoreboard.outs)
        _render_bases(canvas, layout, colors, scoreboard.bases, scoreboard.homerun(), (animation_time % 16) // 5)
        _render_inning_display(canvas, layout, colors, scoreboard.inning)
        _render_play_description(canvas, layout, colors, scoreboard.play_description, text_pos)
    else:
        _render_inning_break(canvas, layout, colors, scoreboard.inning, animation_time)
        pos = _render_due_up(canvas, layout, colors, scoreboard.atbat, text_pos)

    _render_abs_challenges(canvas, layout, colors, scoreboard)
    return pos


# --------------- batter row (top) ---------------
def _render_batter_row(canvas, layout, colors, atbat: AtBat, text_pos):
    stat_pos = __compute_stat_positions(atbat, layout)
    __render_batter_stats(canvas, layout, colors, atbat, stat_pos)
    return __render_batter_name(canvas, layout, colors, atbat, text_pos, stat_pos)


def __compute_stat_positions(atbat: AtBat, layout):
    """Compute stat x positions right-to-left for dynamic spacing."""
    try:
        fw = layout.font("atbat.batter_stats")["size"]["width"]
    except Exception:
        fw = 4

    rbi = str(atbat.rbi) if atbat.rbi is not None else None
    hr = str(atbat.home_runs) if atbat.home_runs is not None else None
    avg = str(atbat.avg) if atbat.avg is not None else None

    # RBI: last char of "RBI" ends at x=126 (1px from right edge)
    rbi_lbl_x = 127 - 3 * fw          # "RBI" starts here
    rbi_val_x = rbi_lbl_x - (len(rbi) * fw if rbi else 0)

    # HR: 1-char gap before RBI value
    hr_end = rbi_val_x - fw
    hr_lbl_x = hr_end - 2 * fw        # "HR" = 2 chars
    hr_val_x = hr_lbl_x - (len(hr) * fw if hr else 0)

    # AVG: 1-char gap before HR value
    avg_end = hr_val_x - fw
    avg_lbl_x = avg_end - 3 * fw      # "AVG" = 3 chars
    avg_val_x = avg_lbl_x - (len(avg) * fw if avg else 0)

    return {
        "avg": avg, "avg_val_x": avg_val_x, "avg_lbl_x": avg_lbl_x,
        "hr": hr,   "hr_val_x": hr_val_x,   "hr_lbl_x": hr_lbl_x,
        "rbi": rbi, "rbi_val_x": rbi_val_x, "rbi_lbl_x": rbi_lbl_x,
        "fw": fw, "leftmost_x": avg_val_x,
    }


def __render_batter_stats(canvas, layout, colors, atbat: AtBat, pos):
    try:
        font = layout.font("atbat.batter_stats")
        y = layout.coords("atbat.batter_stats")["y"]
    except KeyError:
        return

    val_color = colors.graphics_color("atbat.batter_stats")
    lbl_color = colors.graphics_color("atbat.batter_stats_label")

    if pos["avg"] and pos["avg_val_x"] >= 0:
        graphics.DrawText(canvas, font["font"], pos["avg_val_x"], y, val_color, pos["avg"])
        graphics.DrawText(canvas, font["font"], pos["avg_lbl_x"], y, lbl_color, "AVG")
    if pos["hr"] and pos["hr_val_x"] >= 0:
        graphics.DrawText(canvas, font["font"], pos["hr_val_x"], y, val_color, pos["hr"])
        graphics.DrawText(canvas, font["font"], pos["hr_lbl_x"], y, lbl_color, "HR")
    if pos["rbi"]:
        graphics.DrawText(canvas, font["font"], pos["rbi_val_x"], y, val_color, pos["rbi"])
        graphics.DrawText(canvas, font["font"], pos["rbi_lbl_x"], y, lbl_color, "RBI")


def __render_batter_name(canvas, layout, colors, atbat: AtBat, text_pos, stat_pos):
    # Render batting order in small font
    name_x = layout.coords("atbat.batter")["x"]
    order_drawn = False
    try:
        order_coords = layout.coords("atbat.batter_order")
        order_font = layout.font("atbat.batter_order")
        order_color = colors.graphics_color("atbat.batter_stats")
        if atbat.batting_order is not None:
            order_str = f"{atbat.batting_order}."
            graphics.DrawText(canvas, order_font["font"], order_coords["x"], order_coords["y"], order_color, order_str)
            name_x = order_coords["x"] + len(order_str) * order_font["size"]["width"]
            order_drawn = True
    except KeyError:
        pass

    # Render name in main font, scrolling if too wide
    coords = layout.coords("atbat.batter")
    font = layout.font("atbat.batter")
    color = colors.graphics_color("atbat.batter")
    bgcolor = colors.graphics_color("default.background")

    # scrolling_text masks one font-width to the left of the window; pad name_x
    # by that same amount so the mask never bleeds back over the order/period text
    if order_drawn:
        name_x += font["size"]["width"] - 2

    max_width = max(10, stat_pos["leftmost_x"] - name_x - 2)
    name = atbat.batter

    if len(name) * font["size"]["width"] <= max_width:
        graphics.DrawText(canvas, font["font"], name_x, coords["y"], color, name)
        return 0
    return scrolling_text(canvas, graphics, name_x, coords["y"], max_width,
                          font, color, bgcolor, name, text_pos, center=False)


# --------------- pitcher row (second) ---------------
def _render_pitcher_row(canvas, layout, colors, atbat: AtBat, pitches: Pitches):
    __render_pitcher_name(canvas, layout, colors, atbat)
    __render_pitch_text(canvas, layout, colors, pitches)
    __render_pitch_count_right(canvas, layout, colors, pitches)


def __render_pitcher_name(canvas, layout, colors, atbat: AtBat):
    coords = layout.coords("atbat.pitcher")
    font = layout.font("atbat.pitcher")
    color = colors.graphics_color("atbat.pitcher")
    x, y, total_w = coords["x"], coords["y"], coords["width"]
    fw = font["size"]["width"]

    era = atbat.pitcher_era
    if era:
        try:
            lbl_font = layout.font("atbat.batter_stats")
            lbl_color = colors.graphics_color("atbat.batter_stats_label")
            ew = lbl_font["size"]["width"]
            era_px = (len(era) + 3) * ew   # value + "ERA"
            name_chars = max(1, (total_w - era_px - 1) // fw)
            graphics.DrawText(canvas, font["font"], x, y, color, atbat.pitcher[:name_chars])
            era_x = x + name_chars * fw + 1
            graphics.DrawText(canvas, lbl_font["font"], era_x, y, color, era)
            graphics.DrawText(canvas, lbl_font["font"], era_x + len(era) * ew, y, lbl_color, "ERA")
            return
        except KeyError:
            pass

    max_chars = total_w // fw
    graphics.DrawText(canvas, font["font"], x, y, color, atbat.pitcher[:max_chars])


def __render_pitch_text(canvas, layout, colors, pitches: Pitches):
    coords = layout.coords("atbat.pitch")
    if not coords.get("enabled", False) or not int(pitches.last_pitch_speed):
        return
    font = layout.font("atbat.pitch")
    color = colors.graphics_color("atbat.pitch")

    if coords["desc_length"].lower() == "long":
        pitch_text = f"{pitches.last_pitch_speed} {pitches.last_pitch_type_long}"
    else:
        pitch_text = f"{pitches.last_pitch_speed} {pitches.last_pitch_type}"
    if coords.get("mph", False):
        pitch_text = pitch_text.replace(" ", "mph ", 1)

    try:
        pc_coords = layout.coords("atbat.pitch_count_display")
        pc_font = layout.font("atbat.pitch_count_display")
        pc_width = len(f"P:{pitches.pitch_count}") * pc_font["size"]["width"]
        right_edge = pc_coords["x"] - pc_width - 3
    except KeyError:
        right_edge = 106

    fw = font["size"]["width"]
    x = right_edge - len(pitch_text) * fw
    if x < coords["x"]:
        max_chars = (right_edge - coords["x"]) // fw
        pitch_text = pitch_text[:max_chars]
        x = coords["x"]
    graphics.DrawText(canvas, font["font"], x, coords["y"], color, pitch_text)


def __render_pitch_count_right(canvas, layout, colors, pitches: Pitches):
    try:
        coords = layout.coords("atbat.pitch_count_display")
        if not coords.get("enabled", True):
            return
    except KeyError:
        return
    font = layout.font("atbat.pitch_count_display")
    color = colors.graphics_color("atbat.pitch_count_display")
    text = f"P:{pitches.pitch_count}"
    x = coords["x"] - len(text) * font["size"]["width"]
    graphics.DrawText(canvas, font["font"], x, coords["y"], color, text)


# --------------- divider ---------------
def _render_divider(canvas, layout, colors):
    try:
        divider_y = layout.coords("teams.background.away")["y"] - 1
    except KeyError:
        divider_y = 27
    color = colors.graphics_color("atbat.pitcher")
    graphics.DrawLine(canvas, 0, divider_y, canvas.width - 1, divider_y, color)


# --------------- bases ---------------
def _render_bases(canvas, layout, colors, bases: Bases, home_run, animation):
    base_runners = bases.runners
    base_colors = [
        colors.graphics_color("bases.1B"),
        colors.graphics_color("bases.2B"),
        colors.graphics_color("bases.3B"),
    ]
    base_px = [
        layout.coords("bases.1B"),
        layout.coords("bases.2B"),
        layout.coords("bases.3B"),
    ]
    for base in range(len(base_runners)):
        __render_base_outline(canvas, base_px[base], base_colors[base])
        if base_runners[base] or (home_run and animation == base):
            __render_baserunner(canvas, base_px[base], base_colors[base])


def __render_base_outline(canvas, base, color):
    x, y = base["x"], base["y"]
    size = base["size"]
    half = size // 2
    graphics.DrawLine(canvas, x + half, y, x, y + half, color)
    graphics.DrawLine(canvas, x + half, y, x + size, y + half, color)
    graphics.DrawLine(canvas, x + half, y + size, x, y + half, color)
    graphics.DrawLine(canvas, x + half, y + size, x + size, y + half, color)


def __render_baserunner(canvas, base, color):
    x, y = base["x"], base["y"]
    size = base["size"]
    half = size // 2
    for offset in range(1, half + 1):
        graphics.DrawLine(canvas, x + half - offset, y + size - offset, x + half + offset, y + size - offset, color)
        graphics.DrawLine(canvas, x + half - offset, y + offset, x + half + offset, y + offset, color)


# --------------- count ---------------
def _render_count(canvas, layout, colors, pitches: Pitches):
    font = layout.font("batter_count")
    coords = layout.coords("batter_count")
    color = colors.graphics_color("batter_count")
    text = "{}-{}".format(pitches.balls, pitches.strikes)
    x = coords["x"] - len(text) * font["size"]["width"]
    graphics.DrawText(canvas, font["font"], x, coords["y"], color, text)


# --------------- outs (squares) ---------------
def _render_outs(canvas, layout, colors, outs):
    out_px = [layout.coords(f"outs.{i+1}") for i in range(3)]
    _, fill_colors = __out_colors(colors)
    try:
        inactive = colors.graphics_color("inning.arrow.inactive")
    except KeyError:
        inactive = graphics.Color(80, 70, 20)
    for i, out in enumerate(out_px):
        color = fill_colors[i] if outs.number > i else inactive
        __fill_out_square(canvas, out, color)


def __out_colors(colors):
    outlines, fills = [], []
    for i in range(3):
        c = colors.graphics_color(f"outs.{i+1}")
        outlines.append(c)
        try:
            c = colors.graphics_color(f"outs.fill.{i+1}")
        except KeyError:
            pass
        fills.append(c)
    return outlines, fills


def __render_out_square(canvas, out, color):
    x, y, s = out["x"], out["y"], out["size"]
    graphics.DrawLine(canvas, x, y, x + s - 1, y, color)
    graphics.DrawLine(canvas, x, y + s - 1, x + s - 1, y + s - 1, color)
    graphics.DrawLine(canvas, x, y, x, y + s - 1, color)
    graphics.DrawLine(canvas, x + s - 1, y, x + s - 1, y + s - 1, color)


def __fill_out_square(canvas, out, color):
    x, y, s = out["x"], out["y"], out["size"]
    for dy in range(s):
        graphics.DrawLine(canvas, x, y + dy, x + s - 1, y + dy, color)


# --------------- ABS challenge squares (now using real API data) ---------------
def _render_abs_challenges(canvas, layout, colors, scoreboard: Scoreboard):
    try:
        abs_coords = layout.coords("teams.abs_challenges")
        avail_color = colors.graphics_color("abs_challenges.available")
        used_color = colors.graphics_color("abs_challenges.used")
    except KeyError:
        return

    counts = {
        "away": scoreboard.away_abs_challenges if scoreboard.away_abs_challenges is not None else 2,
        "home": scoreboard.home_abs_challenges if scoreboard.home_abs_challenges is not None else 2,
    }

    for side in ("away", "home"):
        cfg = abs_coords[side]
        if not cfg.get("enabled", True):
            continue
        remaining = counts[side]
        x = cfg["x"]
        size = cfg["size"]
        for i, y in enumerate(cfg["squares"]):
            color = avail_color if i < remaining else used_color
            __draw_challenge_square(canvas, x, y, size, color)


def __draw_challenge_square(canvas, x, y, size, color):
    for dy in range(size):
        graphics.DrawLine(canvas, x, y + dy, x + size - 1, y + dy, color)


# --------------- play description scroll (bottom right) ---------------
def _render_play_description(canvas, layout, colors, description, _text_pos):
    global _play_desc_pos, _play_desc_last
    try:
        coords = layout.coords("atbat.play_description")
    except KeyError:
        return
    if not description:
        _play_desc_pos = None
        _play_desc_last = None
        return

    font = layout.font("atbat.play_description")
    color = colors.graphics_color("atbat.play_result")
    bgcolor = colors.graphics_color("default.background")
    x, y, w = coords["x"], coords["y"], coords["width"]
    total_px = len(description) * font["size"]["width"]

    if description != _play_desc_last:
        _play_desc_pos = x + w
        _play_desc_last = description

    scrolling_text(canvas, graphics, x, y, w, font, color, bgcolor,
                   description, _play_desc_pos, center=False, force_scroll=True)

    _play_desc_pos -= 1
    if _play_desc_pos + total_px < x:
        _play_desc_pos = x + w


# --------------- inning display ---------------
def _render_inning_display(canvas, layout, colors, inning: Inning):
    __render_inning_number(canvas, layout, colors, inning)
    __render_inning_arrows(canvas, layout, colors, inning)


def __render_inning_number(canvas, layout, colors, inning: Inning):
    coords = layout.coords("inning.number")
    font = layout.font("inning.number")
    color = colors.graphics_color("inning.number")
    num_str = str(inning.number)

    # Dynamically center between the two arrows
    up_y = layout.coords("inning.arrow.up")["y"]
    down_y = layout.coords("inning.arrow.down")["y"]
    size = layout.coords("inning.arrow")["size"]
    up_base = up_y + size - 1
    down_base = down_y - size + 1
    space = down_base - up_base - 1
    font_h = font["size"]["height"]
    center_y = up_base + 1 + (space - font_h) // 2 + font_h

    x = coords["x"] - len(num_str) * font["size"]["width"]
    graphics.DrawText(canvas, font["font"], x, center_y, color, num_str)


def __render_inning_arrows(canvas, layout, colors, inning: Inning):
    arrow_coords = layout.coords("inning.arrow")
    size = arrow_coords["size"]
    is_top = inning.state == Inning.TOP

    up = layout.coords("inning.arrow.up")
    down = layout.coords("inning.arrow.down")

    active_up = colors.graphics_color("inning.arrow.up")
    active_down = colors.graphics_color("inning.arrow.down")
    try:
        inactive = colors.graphics_color("inning.arrow.inactive")
    except KeyError:
        inactive = graphics.Color(80, 70, 20)

    up_color = active_up if is_top else inactive
    for offset in range(size):
        graphics.DrawLine(canvas, up["x"] - offset, up["y"] + offset,
                          up["x"] + offset, up["y"] + offset, up_color)

    down_color = active_down if not is_top else inactive
    for offset in range(size):
        graphics.DrawLine(canvas, down["x"] - offset, down["y"] - offset,
                          down["x"] + offset, down["y"] - offset, down_color)


# --------------- inning break (items 7 & 8) ---------------
def _render_inning_break(canvas, layout, colors, inning: Inning, animation_time):
    """During break: flash the upcoming half's arrow, show empty bases/outs."""
    try:
        active_color = colors.graphics_color("inning.arrow.up")
        inactive = colors.graphics_color("inning.arrow.inactive")
    except KeyError:
        active_color = graphics.Color(255, 235, 59)
        inactive = graphics.Color(80, 70, 20)

    # Determine which arrow to flash: Middle→next is Bottom, End→next is Top
    flash_up = (inning.state == Inning.END)
    flash_on = int(time.time()) % 2 == 0  # 1Hz slow flash

    arrow_coords = layout.coords("inning.arrow")
    size = arrow_coords["size"]
    up = layout.coords("inning.arrow.up")
    down = layout.coords("inning.arrow.down")

    up_color = (active_color if flash_on else inactive) if flash_up else inactive
    for offset in range(size):
        graphics.DrawLine(canvas, up["x"] - offset, up["y"] + offset,
                          up["x"] + offset, up["y"] + offset, up_color)

    down_color = inactive if flash_up else (active_color if flash_on else inactive)
    for offset in range(size):
        graphics.DrawLine(canvas, down["x"] - offset, down["y"] - offset,
                          down["x"] + offset, down["y"] - offset, down_color)

    # Inning number (static)
    __render_inning_number(canvas, layout, colors, inning)

    # Empty bases (inactive color, no runners)
    for base in ("1B", "2B", "3B"):
        __render_base_outline(canvas, layout.coords(f"bases.{base}"), inactive)

    # Empty outs (3 squares, unfilled)
    for i in range(3):
        __render_out_square(canvas, layout.coords(f"outs.{i+1}"), inactive)


def _render_due_up(canvas, layout, colors, atbat: AtBat, text_pos):
    """Show due-up batters as a single scrolling line in the batter row."""
    coords = layout.coords("inning.break.due_up.leadoff")
    font = layout.font("inning.break.due_up.leadoff")
    color = colors.graphics_color("inning.break.due_up_names")
    bgcolor = colors.graphics_color("default.background")

    names = [n for n in [atbat.batter, atbat.onDeck, atbat.inHole] if n]
    due_up_text = "Due up: " + "  ·  ".join(names)

    return scrolling_text(
        canvas, graphics,
        coords["x"], coords["y"], canvas.width - coords["x"],
        font, color, bgcolor, due_up_text, text_pos, center=False,
    )
