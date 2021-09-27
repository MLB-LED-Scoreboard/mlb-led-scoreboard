try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

from data.config.color import Color
from data.config.layout import Layout
from data.scoreboard import Scoreboard
from data.scoreboard.atbat import AtBat
from data.scoreboard.bases import Bases
from data.scoreboard.inning import Inning
from data.scoreboard.pitches import Pitches
from renderers import scrollingtext
from renderers.games import nohitter


def render_live_game(canvas, layout: Layout, colors: Color, scoreboard: Scoreboard, text_pos, animation_time):
    pos = 0

    if scoreboard.inning.state == Inning.TOP or scoreboard.inning.state == Inning.BOTTOM:

        pos = _render_at_bat(
            canvas,
            layout,
            colors,
            scoreboard.atbat,
            text_pos,
            scoreboard.strikeout(),
            scoreboard.strikeout_looking(),
            (animation_time // 6) % 2,
        )

        # Check if we're deep enough into a game and it's a no hitter or perfect game
        should_display_nohitter = layout.coords("nohitter")["innings_until_display"]
        if scoreboard.inning.number > should_display_nohitter:
            if layout.state_is_nohitter():
                nohitter.render_nohit_text(canvas, layout, colors)

        _render_count(canvas, layout, colors, scoreboard.pitches)
        _render_outs(canvas, layout, colors, scoreboard.outs)
        _render_bases(canvas, layout, colors, scoreboard.bases, scoreboard.homerun(), (animation_time % 16) // 5)

        _render_inning_display(canvas, layout, colors, scoreboard.inning)
    else:
        _render_inning_break(canvas, layout, colors, scoreboard.inning)
        _render_due_up(canvas, layout, colors, scoreboard.atbat)

    return pos


# --------------- at-bat ---------------
def _render_at_bat(canvas, layout, colors, atbat: AtBat, text_pos, strikeout, looking, animation):
    plength = __render_pitcher_text(canvas, layout, colors, atbat.pitcher, text_pos)
    if strikeout:
        if animation:
            __render_strikeout(canvas, layout, colors, looking)
        return plength
    else:
        blength = __render_batter_text(canvas, layout, colors, atbat.batter, text_pos)
        return max(plength, blength)


def __render_strikeout(canvas, layout, colors, looking):
    coords = layout.coords("atbat.strikeout")
    color = colors.graphics_color("atbat.strikeout")
    font = layout.font("atbat.strikeout")
    text = "ꓘ" if looking else "K"
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, text)


def __render_batter_text(canvas, layout, colors, batter, text_pos):
    coords = layout.coords("atbat.batter")
    color = colors.graphics_color("atbat.batter")
    font = layout.font("atbat.batter")
    bgcolor = colors.graphics_color("default.background")
    offset = coords.get("offset", 0)
    pos = scrollingtext.render_text(
        canvas,
        coords["x"] + font["size"]["width"] * 3,
        coords["y"],
        coords["width"],
        font,
        color,
        bgcolor,
        batter,
        text_pos + offset,
    )
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, "AB:")
    return pos


def __render_pitcher_text(canvas, layout, colors, pitcher, text_pos):
    coords = layout.coords("atbat.pitcher")
    color = colors.graphics_color("atbat.pitcher")
    font = layout.font("atbat.pitcher")
    bgcolor = colors.graphics_color("default.background")
    pos = scrollingtext.render_text(
        canvas,
        coords["x"] + font["size"]["width"] * 2,
        coords["y"],
        coords["width"],
        font,
        color,
        bgcolor,
        pitcher,
        text_pos,
    )
    graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, "P:")
    return pos


# --------------- bases ---------------
def _render_bases(canvas, layout, colors, bases: Bases, home_run, animation):
    base_runners = bases.runners
    base_colors = []
    base_colors.append(colors.graphics_color("bases.1B"))
    base_colors.append(colors.graphics_color("bases.2B"))
    base_colors.append(colors.graphics_color("bases.3B"))

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
def _render_outs(canvas, layout, colors, outs):
    out_px = []
    out_px.append(layout.coords("outs.1"))
    out_px.append(layout.coords("outs.2"))
    out_px.append(layout.coords("outs.3"))

    out_colors = []
    out_colors.append(colors.graphics_color("outs.1"))
    out_colors.append(colors.graphics_color("outs.2"))
    out_colors.append(colors.graphics_color("outs.3"))

    for out in range(len(out_px)):
        __render_out_circle(canvas, out_px[out], out_colors[out])
        # Fill in the circle if that out has occurred
        if outs.number > out:
            __fill_out_circle(canvas, out_px[out], out_colors[out])


def __render_out_circle(canvas, out, color):
    x, y, size = (out["x"], out["y"], out["size"])
    graphics.DrawLine(canvas, x, y, x + size, y, color)
    graphics.DrawLine(canvas, x, y, x, y + size, color)
    graphics.DrawLine(canvas, x + size, y + size, x, y + size, color)
    graphics.DrawLine(canvas, x + size, y + size, x + size, y, color)


def __fill_out_circle(canvas, out, color):
    size = out["size"]
    x, y = (out["x"], out["y"])
    for y_offset in range(size):
        graphics.DrawLine(canvas, x, y + y_offset, x + size, y + y_offset, color)


# --------------- inning information ---------------
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


def _render_due_up(canvas, layout, colors, atbat: AtBat):
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

    batter_font = layout.font("inning.break.due_up.leadoff")
    batter_color = colors.graphics_color("inning.break.due_up_names")

    leadoff = layout.coords("inning.break.due_up.leadoff")
    on_deck = layout.coords("inning.break.due_up.on_deck")
    in_hole = layout.coords("inning.break.due_up.in_hole")
    graphics.DrawText(canvas, batter_font["font"], leadoff["x"], leadoff["y"], batter_color, atbat.batter)
    graphics.DrawText(canvas, batter_font["font"], on_deck["x"], on_deck["y"], batter_color, atbat.onDeck)
    graphics.DrawText(canvas, batter_font["font"], in_hole["x"], in_hole["y"], batter_color, atbat.inHole)


def _render_inning_display(canvas, layout, colors, inning: Inning):
    __render_number(canvas, layout, colors, inning)
    __render_inning_half(canvas, layout, colors, inning)


def __render_number(canvas, layout, colors, inning):
    number_color = colors.graphics_color("inning.number")
    coords = layout.coords("inning.number")
    font = layout.font("inning.number")
    pos_x = coords["x"] - (len(str(inning.number)) * font["size"]["width"])
    graphics.DrawText(canvas, font["font"], pos_x, coords["y"], number_color, str(inning.number))


def __render_inning_half(canvas, layout, colors, inning):
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
