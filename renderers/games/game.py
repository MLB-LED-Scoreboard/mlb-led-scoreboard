from bullpen.util import scrolling_text

from data import status
from driver import graphics
from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard import Scoreboard
from data.scoreboard.atbat import AtBat
from data.scoreboard.bases import Bases
from data.scoreboard.inning import Inning
from data.scoreboard.pitches import Pitches
from data.plays import PLAY_RESULTS

from renderers.games import nohitter


def render_live_game(canvas, layout: Layout, colors: Color, scoreboard: Scoreboard, text_pos, animation_time):
    # One phase for everything on the live screen that pulses: the play-result flash
    # and the inning arrow blink.
    animation = (animation_time // 6) % 2
    pos = 0
    if not status.is_inning_break(scoreboard.inning.state):
        pos = _render_at_bat(
            canvas,
            layout,
            colors,
            scoreboard.atbat,
            text_pos,
            scoreboard.play_result,
            animation,
            scoreboard.pitches,
        )

        # Check if we're deep enough into a game and it's a no hitter or perfect game
        should_display_nohitter = layout.coords("nohitter")["innings_until_display"]
        if scoreboard.inning.number > should_display_nohitter:
            if layout.state_is_nohitter():
                nohitter.render_nohit_text(canvas, layout, colors)

        _render_count(canvas, layout, colors, scoreboard.pitches)
        _render_outs(canvas, layout, colors, scoreboard.outs)
        _render_bases(canvas, layout, colors, scoreboard.bases, scoreboard.homerun(), (animation_time % 16) // 5)

        pos = max(pos, __render_play_description(canvas, layout, colors, scoreboard.play_description, text_pos))

        _render_inning_display(canvas, layout, colors, scoreboard.inning, animation)

    elif __break_shows_field(layout):
        __render_dimmed_field(canvas, layout, colors, scoreboard)
        _render_inning_display(canvas, layout, colors, scoreboard.inning, animation)
        pos = _render_due_up(canvas, layout, colors, scoreboard.atbat, text_pos)

    else:
        _render_inning_break(canvas, layout, colors, scoreboard.inning)
        pos = _render_due_up(canvas, layout, colors, scoreboard.atbat, text_pos)

    return pos


# --------------- at-bat ---------------
def _render_at_bat(canvas, layout, colors, atbat: AtBat, text_pos, play_result, animation, pitches: Pitches):
    plength = __render_pitcher_text(canvas, layout, colors, atbat, pitches, text_pos)
    __render_pitch_text(canvas, layout, colors, pitches)
    __render_pitch_count(canvas, layout, colors, pitches)
    if play_result in PLAY_RESULTS and __should_render_play_result(play_result, layout):
        if animation:
            __render_play_result(canvas, layout, colors, play_result)
        return plength
    else:
        blength = __render_batter_text(canvas, layout, colors, atbat, text_pos)
        return max(plength, blength)


def __should_render_play_result(play_result, layout):
    if "strikeout" in play_result:
        coords = layout.coords("atbat.strikeout")
    else:
        coords = layout.coords("atbat.play_result")
    return coords["enabled"]


def __render_play_result(canvas, layout, colors, play_result):
    if "strikeout" in play_result:
        color = colors.graphics_color("atbat.strikeout")
        coords = layout.coords("atbat.strikeout")
        font = layout.font("atbat.strikeout")
    else:
        color = colors.graphics_color("atbat.play_result")
        coords = layout.coords("atbat.play_result")
        font = layout.font("atbat.play_result")
    try:
        text = PLAY_RESULTS[play_result][coords["desc_length"].lower()]
    except KeyError:
        return
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, text)


def __optional(layout, key):
    """Return coords for an optional element, or None when absent/disabled.

    Keeps every addition opt-in: layouts that don't define the key (or set
    "enabled": false) render exactly as they did before.
    """
    try:
        coords = layout.coords(key)
    except KeyError:
        return None
    return coords if coords.get("enabled", False) else None


def __looped_pos(layout, text_pos, x, width, text, font):
    """Wrap the shared scroll position onto one row's own cycle.

    Every scrolling row is driven by the single position MainRenderer decrements
    once per frame, and the rotation holds until the longest of them has been read.
    Without a wrap the short rows pay for the long one: a batter's name alongside a
    60-character play description scrolls off in a couple of seconds and then leaves
    its row blank for the twenty the description still needs.

    The cycle is anchored to the loop point -- the value MainRenderer resets the
    shared position to -- rather than to the raw position, so each row begins its
    pass just off its own right edge and scrolls on from there. Anchoring to the
    position itself lands every row at whatever phase the counter happens to be in:
    the play line, whose slot ends at the far edge of the board, started 13px into
    its own window with the first character already showing.
    """
    cycle = len(text) * font["size"]["width"] + width
    elapsed = (layout.coords("atbat")["loop"] - text_pos) % cycle
    return x + width - elapsed


def __break_shows_field(layout):
    """Whether the break screen keeps the field furniture instead of "Mid 5th".

    Off unless a layout asks for it, and it has to be asked for explicitly rather
    than inferred from the coordinates being present: every stock layout stacks the
    due-up names across the space the diamond occupies, so drawing both would put
    text on top of the diamond.
    """
    try:
        return layout.coords("inning.break").get("show_field", False)
    except KeyError:
        return False


def __render_dimmed_field(canvas, layout, colors, scoreboard: Scoreboard):
    """The diamond and out markers, all in one dim colour."""
    try:
        idle = colors.graphics_color("inning.break.inactive")
    except KeyError:
        return
    _render_bases(canvas, layout, colors, scoreboard.bases, False, 0, override_color=idle)
    _render_outs(canvas, layout, colors, scoreboard.outs, override_color=idle)


def __batter_stat_positions(layout, atbat: AtBat):
    """Lay AVG / HR / RBI out right-to-left so they always fit the panel."""
    font = layout.font("atbat.batter_stats")
    fw = font["size"]["width"]
    right = layout.width - 1

    rbi = str(atbat.rbi) if atbat.rbi is not None else None
    hr = str(atbat.home_runs) if atbat.home_runs is not None else None
    avg = str(atbat.avg) if atbat.avg is not None else None

    rbi_lbl_x = right - 3 * fw
    rbi_val_x = rbi_lbl_x - (len(rbi) * fw if rbi else 0)
    hr_lbl_x = (rbi_val_x - fw) - 2 * fw
    hr_val_x = hr_lbl_x - (len(hr) * fw if hr else 0)
    avg_lbl_x = (hr_val_x - fw) - 3 * fw
    avg_val_x = avg_lbl_x - (len(avg) * fw if avg else 0)

    return {
        "font": font,
        "avg": avg,
        "avg_val_x": avg_val_x,
        "avg_lbl_x": avg_lbl_x,
        "hr": hr,
        "hr_val_x": hr_val_x,
        "hr_lbl_x": hr_lbl_x,
        "rbi": rbi,
        "rbi_val_x": rbi_val_x,
        "rbi_lbl_x": rbi_lbl_x,
        "leftmost_x": avg_val_x,
    }


def __render_batter_stats(canvas, layout, colors, atbat: AtBat):
    """Season AVG / HR / RBI on the batter row. No-op unless enabled."""
    coords = __optional(layout, "atbat.batter_stats")
    if coords is None:
        return
    pos = __batter_stat_positions(layout, atbat)
    font = pos["font"]
    y = coords["y"]
    val_color = colors.graphics_color("atbat.batter_stats")
    lbl_color = colors.graphics_color("atbat.batter_stats_label")

    for key, label in (("avg", "AVG"), ("hr", "HR"), ("rbi", "RBI")):
        if pos[key] and pos[f"{key}_val_x"] >= 0:
            graphics.DrawText(canvas, font["font"], pos[f"{key}_val_x"], y, val_color, pos[key])
            graphics.DrawText(canvas, font["font"], pos[f"{key}_lbl_x"], y, lbl_color, label)


def __render_batter_order(canvas, layout, colors, atbat: AtBat):
    """Batting-order number ("7.") ahead of the batter name. No-op unless enabled."""
    coords = __optional(layout, "atbat.batter_order")
    if coords is None or atbat.batter_order is None:
        return
    font = layout.font("atbat.batter_order")
    color = colors.graphics_color("atbat.batter_stats")
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, f"{atbat.batter_order}.")


def __batter_order_name_x(layout, atbat: AtBat):
    """Where the name starts when the order number replaces the "AB:" label.

    The order text ends with a period, whose right bearing already reads as a gap,
    so only 1px is added -- the previous `fw - 2` left a visible 6px hole on a row
    where every pixel is a character of the batter's name.
    """
    coords = __optional(layout, "atbat.batter_order")
    if coords is None or atbat.batter_order is None:
        return None
    font = layout.font("atbat.batter_order")
    return coords["x"] + len(f"{atbat.batter_order}.") * font["size"]["width"] + 1


def __render_play_description(canvas, layout, colors, description, text_pos):
    """Draw the play-by-play line: centred if it fits, else scrolled.

    Shares the renderer's scroll position with the batter and pitcher rows rather
    than tracking its own, so there is one thing advancing the text per frame.
    scrolling_text() draws a description that already fits in place -- "Mound
    visit.", "Wild pitch." are common and scrolling them is just harder to read --
    and returns a width only while it is actually scrolling, which is what holds
    the rotation until the line has been read.
    """
    coords = __optional(layout, "atbat.play_description")
    if coords is None or not description:
        return 0

    font = layout.font("atbat.play_description")
    x, width = coords["x"], coords["width"]
    return scrolling_text(
        canvas,
        graphics,
        x,
        coords["y"],
        width,
        font,
        colors.graphics_color("atbat.play_result"),
        colors.graphics_color("default.background"),
        description,
        __looped_pos(layout, text_pos, x, width, description, font),
    )


def __render_batter_text(canvas, layout, colors, atbat: AtBat, text_pos):
    coords = layout.coords("atbat.batter")
    color = colors.graphics_color("atbat.batter")
    font = layout.font("atbat.batter")
    bgcolor = colors.graphics_color("default.background")
    offset = coords.get("offset", 0)
    fw = font["size"]["width"]

    # With a batting-order number the "AB:" label is redundant, so it is replaced by
    # the number and the name starts after it.
    order_name_x = __batter_order_name_x(layout, atbat)
    name_x = coords["x"] + fw * 3 if order_name_x is None else order_name_x

    width = coords["width"]
    if __optional(layout, "atbat.batter_stats") is not None:
        # 2px of clearance before the stat column rather than 5, for the same
        # reason: it buys another character and the period-to-digit transition
        # there is already legible.
        width = max(10, __batter_stat_positions(layout, atbat)["leftmost_x"] - name_x - 2)

    pos = scrolling_text(
        canvas,
        graphics,
        name_x,
        coords["y"],
        width,
        font,
        color,
        bgcolor,
        atbat.batter,
        __looped_pos(layout, text_pos + offset, name_x, width, atbat.batter, font),
        center=False,
    )

    # Everything neighbouring the name is drawn after it. scrolling_text() blanks a
    # whole character cell either side of its window to hide partial glyphs, and
    # this row butts up against both neighbours on purpose, so the blanking reaches
    # into them -- it was eating the period off "7." and off ".267".
    __render_batter_order(canvas, layout, colors, atbat)
    __render_batter_stats(canvas, layout, colors, atbat)
    if order_name_x is None:
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, "AB:")
    return pos


def __render_pitcher_text(canvas, layout, colors, atbat: AtBat, pitches: Pitches, text_pos):
    coords = layout.coords("atbat.pitcher")
    color = colors.graphics_color("atbat.pitcher")
    font = layout.font("atbat.pitcher")
    bgcolor = colors.graphics_color("default.background")
    fw = font["size"]["width"]
    pitcher = atbat.pitcher

    pitch_count = layout.coords("atbat.pitch_count")
    if pitch_count["enabled"] and pitch_count["append_pitcher_name"]:
        pitcher += f" ({pitches.pitch_count})"

    # Optional season ERA, aligned with the batter's stat column above it.
    stats = __optional(layout, "atbat.batter_stats")
    era_x = None
    if stats is not None and stats.get("show_era", False) and atbat.pitcher_era:
        pos_info = __batter_stat_positions(layout, atbat)
        lbl_font = pos_info["font"]
        ew = lbl_font["size"]["width"]
        era_x = pos_info["leftmost_x"]
        graphics.DrawText(canvas, lbl_font["font"], era_x, coords["y"], color, atbat.pitcher_era)
        graphics.DrawText(
            canvas,
            lbl_font["font"],
            era_x + len(atbat.pitcher_era) * ew,
            coords["y"],
            colors.graphics_color("atbat.batter_stats_label"),
            "ERA",
        )

    name_x = coords["x"] if era_x is not None else coords["x"] + fw * 2
    width = max(fw, era_x - name_x - fw - 1) if era_x is not None else coords["width"]

    pos = scrolling_text(
        canvas,
        graphics,
        name_x,
        coords["y"],
        width,
        font,
        color,
        bgcolor,
        pitcher,
        __looped_pos(layout, text_pos, name_x, width, pitcher, font),
        center=False,
    )
    if era_x is None:
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, "P:")
    return pos


def __render_pitch_text(canvas, layout, colors, pitches: Pitches):
    coords = layout.coords("atbat.pitch")
    color = colors.graphics_color("atbat.pitch")
    font = layout.font("atbat.pitch")
    if int(pitches.last_pitch_speed) and coords["enabled"]:
        mph = " "
        if coords["mph"]:
            mph = "mph "
        if coords["desc_length"].lower() == "long":
            pitch_text = str(pitches.last_pitch_speed) + mph + pitches.last_pitch_type_long
        elif coords["desc_length"].lower() == "short":
            pitch_text = str(pitches.last_pitch_speed) + mph + pitches.last_pitch_type
        else:
            pitch_text = ""
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, pitch_text)


def __render_pitch_count(canvas, layout, colors, pitches: Pitches):
    coords = layout.coords("atbat.pitch_count")
    color = colors.graphics_color("atbat.pitch_count")
    font = layout.font("atbat.pitch_count")
    if coords["enabled"] and not coords["append_pitcher_name"]:
        pitch_count = f"{pitches.pitch_count}P"
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, pitch_count)


# --------------- bases ---------------
def _render_bases(canvas, layout, colors, bases: Bases, home_run, animation, override_color=None):
    """`override_color` draws every base in one colour.

    Used by the inning break, which keeps the diamond on screen for context but
    dimmed, since nobody is on base between halves of an inning.
    """
    base_runners = bases.runners
    if override_color is not None:
        base_colors = [override_color] * 3
    else:
        base_colors = [colors.graphics_color(f"bases.{b}") for b in ("1B", "2B", "3B")]

    base_px = []
    base_px.append(layout.coords("bases.1B"))
    base_px.append(layout.coords("bases.2B"))
    base_px.append(layout.coords("bases.3B"))

    for base in range(len(base_runners)):
        __render_base_outline(canvas, base_px[base], base_colors[base])

        # Fill in the base if there's currently a baserunner or cycle if theres a homer
        if base_runners[base] or (home_run and animation == base):
            __render_baserunner(canvas, base_px[base], base_colors[base])


def __render_base_outline(canvas, base, color):
    x, y = (base["x"], base["y"])
    size = base["size"]
    half = abs(size // 2)
    graphics.DrawLine(canvas, x + half, y, x, y + half, color)
    graphics.DrawLine(canvas, x + half, y, x + size, y + half, color)
    graphics.DrawLine(canvas, x + half, y + size, x, y + half, color)
    graphics.DrawLine(canvas, x + half, y + size, x + size, y + half, color)


def __render_baserunner(canvas, base, color):
    x, y = (base["x"], base["y"])
    size = base["size"]
    half = abs(size // 2)
    for offset in range(1, half + 1):
        graphics.DrawLine(canvas, x + half - offset, y + size - offset, x + half + offset, y + size - offset, color)
        graphics.DrawLine(canvas, x + half - offset, y + offset, x + half + offset, y + offset, color)


# --------------- count ---------------
def _render_count(canvas, layout, colors, pitches: Pitches):
    font = layout.font("batter_count")
    coords = layout.coords("batter_count")
    pitches_color = colors.graphics_color("batter_count")
    batter_count_text = "{}-{}".format(pitches.balls, pitches.strikes)
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], pitches_color, batter_count_text)


# --------------- outs ---------------
def __out_colors(colors, override_color=None):
    if override_color is not None:
        return [override_color] * 3, [override_color] * 3

    outlines = []
    fills = []
    for i in range(3):
        color = colors.graphics_color(f"outs.{i+1}")
        outlines.append(color)
        try:
            color = colors.graphics_color(f"outs.fill.{i+1}")
        except KeyError:
            pass
        fills.append(color)
    return outlines, fills


def _render_outs(canvas, layout, colors, outs, override_color=None):
    out_px = []
    out_px.append(layout.coords("outs.1"))
    out_px.append(layout.coords("outs.2"))
    out_px.append(layout.coords("outs.3"))

    out_colors, fill_colors = __out_colors(colors, override_color)

    for out in range(len(out_px)):
        __render_out_circle(canvas, out_px[out], out_colors[out])
        # Fill in the circle if that out has occurred
        if outs.number > out:
            __fill_out_circle(canvas, out_px[out], fill_colors[out])


def __render_out_circle(canvas, out, color):
    x, y, size = (out["x"], out["y"], out["size"])

    graphics.DrawLine(canvas, x, y, x + size, y, color)
    graphics.DrawLine(canvas, x, y, x, y + size, color)
    graphics.DrawLine(canvas, x + size, y + size, x, y + size, color)
    graphics.DrawLine(canvas, x + size, y + size, x + size, y, color)


def __fill_out_circle(canvas, out, color):
    size = out["size"]
    x, y = (out["x"], out["y"])
    x += 1
    y += 1
    size -= 1
    for y_offset in range(size):
        graphics.DrawLine(canvas, x, y + y_offset, x + size - 1, y + y_offset, color)


# --------------- inning information ---------------
def __due_up_line(atbat: AtBat) -> str:
    """ "Due Up: 8. Callahan, 9. Peck, 1. McGonigle"

    The order number matters more here than during an at-bat: the point of the
    break screen is who is coming, and the spot in the order is how you know
    whether the top of the lineup is up next.
    """
    parts = []
    for order, name in (
        (atbat.batter_order, atbat.batter),
        (atbat.on_deck_order, atbat.on_deck),
        (atbat.in_hole_order, atbat.in_hole),
    ):
        if not name:
            continue
        parts.append(f"{order}. {name}" if order is not None else name)
    return "Due Up: " + ", ".join(parts) if parts else ""


def _render_due_up(canvas, layout, colors, atbat: AtBat, text_pos):
    # One scrolling line, when the layout asks for it. The stacked three-line
    # form below needs a tall block and a big font, which does not suit a board
    # where the teams already own the bottom half.
    single = __optional(layout, "inning.break.due_up.scroll")
    if single is not None:
        return scrolling_text(
            canvas,
            graphics,
            single["x"],
            single["y"],
            single["width"],
            layout.font("inning.break.due_up.scroll"),
            colors.graphics_color("inning.break.due_up_names"),
            colors.graphics_color("default.background"),
            __due_up_line(atbat),
            text_pos,
            center=False,
        )

    batter_font = layout.font("inning.break.due_up.leadoff")
    batter_color = colors.graphics_color("inning.break.due_up_names")

    leadoff = layout.coords("inning.break.due_up.leadoff")
    on_deck = layout.coords("inning.break.due_up.on_deck")
    in_hole = layout.coords("inning.break.due_up.in_hole")
    background = colors.graphics_color("default.background")

    p1 = scrolling_text(
        canvas,
        graphics,
        leadoff["x"],
        leadoff["y"],
        leadoff["width"],
        batter_font,
        batter_color,
        background,
        atbat.batter,
        text_pos,
        center=False,
    )
    p2 = scrolling_text(
        canvas,
        graphics,
        on_deck["x"],
        on_deck["y"],
        on_deck["width"],
        batter_font,
        batter_color,
        background,
        atbat.on_deck,
        text_pos,
        center=False,
    )
    p3 = scrolling_text(
        canvas,
        graphics,
        in_hole["x"],
        in_hole["y"],
        in_hole["width"],
        batter_font,
        batter_color,
        background,
        atbat.in_hole,
        text_pos,
        center=False,
    )

    due_font = layout.font("inning.break.due_up.due")
    due_color = colors.graphics_color("inning.break.due_up")

    due = layout.coords("inning.break.due_up.due")
    up = layout.coords("inning.break.due_up.up")
    graphics.DrawText(canvas, due_font["font"], due["x"], due["y"], due_color, "Due")
    graphics.DrawText(canvas, due_font["font"], up["x"], up["y"], due_color, "Up:")

    divider = layout.coords("inning.break.due_up.divider")
    if divider["draw"]:
        graphics.DrawLine(
            canvas,
            divider["x"],
            divider["y_start"],
            divider["x"],
            divider["y_end"],
            colors.graphics_color("inning.break.due_up_divider"),
        )

    return max(p1, p2, p3)


def _render_inning_break(canvas, layout, colors, inning: Inning):

    text_font = layout.font("inning.break.text")
    num_font = layout.font("inning.break.number")
    text_coords = layout.coords("inning.break.text")
    num_coords = layout.coords("inning.break.number")
    color = colors.graphics_color("inning.break.text")
    text = inning.state
    if text == "Middle":
        text = "Mid"
    num = inning.ordinal
    graphics.DrawText(canvas, text_font["font"], text_coords["x"], text_coords["y"], color, text)
    graphics.DrawText(canvas, num_font["font"], num_coords["x"], num_coords["y"], color, num)


def _render_inning_display(canvas, layout, colors, inning: Inning, blink_on=False):
    __render_inning_number(canvas, layout, colors, inning)
    __render_inning_half(canvas, layout, colors, inning, blink_on)


def __render_inning_half(canvas, layout, colors, inning: Inning, blink_on=False):
    """The arrow showing which half of the inning is being played.

    Two placements, chosen by `inning.arrow.stacked`:

    off (default)  one arrow, positioned relative to the inning number by
                   `x_offset`/`y_offset`, drawn in inning.arrow.up/down.
    on             both arrows drawn at their absolute `x`/`y`, the active half in
                   inning.arrow.active and the other dimmed, so the indicator holds
                   the same shape all game instead of jumping between two positions.

    Stacked placement is what makes the arrows usable on a break screen, where the
    inning number they would otherwise hang off is not necessarily there.
    """
    if layout.coords("inning.arrow").get("stacked", False):
        __render_stacked_arrows(canvas, layout, colors, inning, blink_on)
    else:
        __render_offset_arrow(canvas, layout, colors, inning)


def __render_offset_arrow(canvas, layout, colors, inning: Inning):
    font = layout.font("inning.number")
    num_coords = layout.coords("inning.number")
    arrow_coords = layout.coords("inning.arrow")
    inning_size = len(str(inning.number)) * font["size"]["width"]
    size = arrow_coords["size"]
    top = inning.state == Inning.TOP
    if top:
        x = num_coords["x"] - inning_size + arrow_coords["up"]["x_offset"]
        y = num_coords["y"] + arrow_coords["up"]["y_offset"]
        dir = 1
    else:
        x = num_coords["x"] - inning_size + arrow_coords["down"]["x_offset"]
        y = num_coords["y"] + arrow_coords["down"]["y_offset"]
        dir = -1

    keypath = "inning.arrow.up" if top else "inning.arrow.down"
    color = colors.graphics_color(keypath)
    for offset in range(size):
        graphics.DrawLine(canvas, x - offset, y + (offset * dir), x + offset, y + (offset * dir), color)


def __render_stacked_arrows(canvas, layout, colors, inning: Inning, blink_on):
    up = layout.coords("inning.arrow.up")
    down = layout.coords("inning.arrow.down")
    size = layout.coords("inning.arrow")["size"]
    try:
        active = colors.graphics_color("inning.arrow.active")
        inactive = colors.graphics_color("inning.arrow.inactive")
    except KeyError:
        return

    if status.is_inning_break(inning.state):
        # Blink whichever half is about to be played. Middle means the bottom is
        # next; End means the top of the next inning is.
        upcoming_is_top = inning.state == Inning.END
        up_color = (active if blink_on else inactive) if upcoming_is_top else inactive
        down_color = inactive if upcoming_is_top else (active if blink_on else inactive)
    else:
        is_top = inning.state == Inning.TOP
        up_color = active if is_top else inactive
        down_color = inactive if is_top else active

    # Tip of each arrow is at its (x, y): the up arrow widens downwards from there,
    # the down arrow upwards.
    for offset in range(size):
        graphics.DrawLine(canvas, up["x"] - offset, up["y"] + offset, up["x"] + offset, up["y"] + offset, up_color)
    for offset in range(size):
        graphics.DrawLine(
            canvas, down["x"] - offset, down["y"] - offset, down["x"] + offset, down["y"] - offset, down_color
        )


def __render_inning_number(canvas, layout, colors, inning: Inning):
    coords = layout.coords("inning.number")
    font = layout.font("inning.number")
    color = colors.graphics_color("inning.number")
    num_str = str(inning.number)
    pos_x = coords["x"] - len(num_str) * font["size"]["width"]
    graphics.DrawText(canvas, font["font"], pos_x, coords["y"], color, num_str)
