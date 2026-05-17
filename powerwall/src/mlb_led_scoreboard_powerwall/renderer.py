from pathlib import Path
from typing import TYPE_CHECKING, Optional

import bullpen.api as api
from bullpen.util import center_text_position, scrolling_text

from .config import Config
from .data import PowerwallData

_ICONS_DIR = Path(__file__).parent / "icons"


def _load_png(name: str):
    """Load a 32×32 RGBA icon PNG if it exists, otherwise return None."""
    path = _ICONS_DIR / f"{name}.png"
    if path.exists():
        from PIL import Image
        return Image.open(path).convert("RGBA")
    return None

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas

# ── Layout constants (128×64 display) ────────────────────────────────────────
_SOLAR_CX   = 16   # solar icon center x
_HOME_CX    = 64   # home icon center x
_BATT_CX    = 112  # battery/grid icon center x

_SOLAR_IX   = 0    # solar icon left edge
_HOME_IX    = 48   # home icon left edge
_BATT_IX    = 96   # battery/grid icon left edge
_ICON_IY    = 0    # all icons share this top edge

_FLOW_L_X   = 32   # solar→home gap start x
_FLOW_R_X   = 80   # battery→home gap start x
_FLOW_W     = 16   # width of each gap
_FLOW_Y     = 15   # y center of flow dots

_VALUE_Y    = 44   # text baseline for main values (7x13 font)
_BATT_KW_Y  = 54   # text baseline for battery kW row (5x7 font)
_SCROLL_Y   = 63   # text baseline for solar kWh scroll (4x6 font)


class Renderer(api.PluginRenderer["PowerwallData"]):
    def __init__(self, config: Config, layout: api.Layout, colors: api.Color) -> None:
        self.config = config
        self.layout = layout
        self.colors = colors
        self._phase = 0

        self.bg             = colors.graphics_color("powerwall.background")
        self.solar_c        = colors.graphics_color("powerwall.solar_icon")
        self.home_c         = colors.graphics_color("powerwall.home_icon")
        self.batt_c         = colors.graphics_color("powerwall.battery_icon")
        self.fill_high      = colors.graphics_color("powerwall.battery_fill_high")
        self.fill_mid       = colors.graphics_color("powerwall.battery_fill_mid")
        self.fill_low       = colors.graphics_color("powerwall.battery_fill_low")
        self.wave_c         = colors.graphics_color("powerwall.battery_wave")
        self.arrow_c        = colors.graphics_color("powerwall.battery_arrow")
        self.grid_c         = colors.graphics_color("powerwall.grid_icon")
        self.flow_solar_on  = colors.graphics_color("powerwall.solar_flow_active")
        self.flow_solar_off = colors.graphics_color("powerwall.solar_flow_idle")
        self.flow_batt      = colors.graphics_color("powerwall.battery_flow")
        self.flow_grid      = colors.graphics_color("powerwall.grid_flow")
        self.solar_val_c    = colors.graphics_color("powerwall.solar_value")
        self.home_val_c     = colors.graphics_color("powerwall.home_value")
        self.batt_val_c     = colors.graphics_color("powerwall.battery_value")

        self._font       = layout.font("powerwall.value_font")   # 7x13 default
        self._small_font = layout.font("atbat.pitcher")           # 5x7
        self._tiny_font  = layout.font("atbat.batter_stats")      # 4x6

        # Optional user-supplied PNG icons (32×32 RGBA). Falls back to code-drawn.
        self._solar_png       = _load_png("solar")
        self._home_png        = _load_png("home")
        self._grid_png        = _load_png("grid")
        self._batt_frame_png  = _load_png("battery_frame")  # outline only, transparent interior

    def wait_time(self) -> float:
        return 0.1

    def can_render(self, data: PowerwallData) -> bool:
        return True

    def reset(self):
        pass  # keep animation phase continuous across screen transitions

    def render(
        self,
        data: PowerwallData,
        canvas: "Canvas",
        graphics: api.renderer.graphics,
        scrolling_text_pos: int,
    ) -> Optional[int]:
        canvas.Fill(self.bg.red, self.bg.green, self.bg.blue)

        # ── Icons ──────────────────────────────────────────────────────────────
        if self._solar_png:
            self._draw_png(canvas, _SOLAR_IX, _ICON_IY, self._solar_png)
        else:
            self._solar_icon(canvas, graphics, _SOLAR_IX, _ICON_IY)

        if self._home_png:
            self._draw_png(canvas, _HOME_IX, _ICON_IY, self._home_png)
        else:
            self._home_icon(canvas, graphics, _HOME_IX, _ICON_IY)

        if data.is_grid_active:
            if self._grid_png:
                self._draw_png(canvas, _BATT_IX, _ICON_IY, self._grid_png)
            else:
                self._grid_icon(canvas, graphics, _BATT_IX, _ICON_IY)
        else:
            self._battery_icon(
                canvas, graphics, _BATT_IX, _ICON_IY,
                data.charge_pct, data.is_charging, data.is_discharging,
            )

        # ── Flow lines ─────────────────────────────────────────────────────────
        if data.solar_kw > 0.05:
            self._flow(canvas, _FLOW_L_X, _FLOW_W, _FLOW_Y, self.flow_solar_on, rightward=True)
        else:
            self._flow_idle(canvas, _FLOW_L_X, _FLOW_W, _FLOW_Y, self.flow_solar_off)

        if data.is_grid_active:
            self._flow(canvas, _FLOW_R_X, _FLOW_W, _FLOW_Y, self.flow_grid, rightward=False)
        elif data.is_discharging:
            self._flow(canvas, _FLOW_R_X, _FLOW_W, _FLOW_Y, self.flow_batt, rightward=False)

        # ── Main values row ────────────────────────────────────────────────────
        self._value(canvas, graphics, _SOLAR_CX, f"{data.solar_kw:.1f}kW", self.solar_val_c)
        self._value(canvas, graphics, _HOME_CX,  f"{data.home_kw:.1f}kW",  self.home_val_c)

        if data.is_grid_active:
            self._value(canvas, graphics, _BATT_CX, f"-{data.grid_kw:.1f}kW", self.flow_grid)
        else:
            self._value(canvas, graphics, _BATT_CX, f"{int(round(data.charge_pct))}%", self.batt_val_c)

        # ── Battery kW row (always shown when active) ──────────────────────────
        if abs(data.battery_kw) > 0.05:
            batt_kw_text = f"{data.battery_kw:.1f}kW"
            batt_kw_color = self.fill_high if data.is_charging else self.batt_val_c
            self._small_value(canvas, graphics, _BATT_CX, batt_kw_text, batt_kw_color)

        # ── Solar kWh today scroll ─────────────────────────────────────────────
        self._phase = (self._phase + 1) % 480
        if data.solar_kwh_today > 0:
            scroll_text = f"Solar today: {data.solar_kwh_today:.1f} kWh"
            color = self.solar_val_c
            bgcolor = self.bg
            return scrolling_text(canvas, graphics, 0, _SCROLL_Y, canvas.width,
                                  self._tiny_font, color, bgcolor, scroll_text,
                                  scrolling_text_pos, center=False, force_scroll=True)
        return None

    # ── Icon renderers ─────────────────────────────────────────────────────────

    def _solar_icon(self, canvas, graphics, ix, iy):
        c = self.solar_c
        r, g, b = c.red, c.green, c.blue
        cx, cy = ix + 15, iy + 8  # sun center

        # Sun core (3×3)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                canvas.SetPixel(cx + dx, cy + dy, r, g, b)

        # Glow ring at radius 2
        for dx in range(-2, 3):
            canvas.SetPixel(cx + dx, cy - 2, r, g, b)
            canvas.SetPixel(cx + dx, cy + 2, r, g, b)
        for dy in (-1, 0, 1):
            canvas.SetPixel(cx - 2, cy + dy, r, g, b)
            canvas.SetPixel(cx + 2, cy + dy, r, g, b)

        # 8 rays (pixels at radius 3–5)
        for i in range(3, 6):
            canvas.SetPixel(cx,     cy - i, r, g, b)  # N
            canvas.SetPixel(cx,     cy + i, r, g, b)  # S
            canvas.SetPixel(cx - i, cy,     r, g, b)  # W
            canvas.SetPixel(cx + i, cy,     r, g, b)  # E
        for d in (3, 4):
            canvas.SetPixel(cx - d, cy - d, r, g, b)  # NW
            canvas.SetPixel(cx + d, cy - d, r, g, b)  # NE
            canvas.SetPixel(cx - d, cy + d, r, g, b)  # SW
            canvas.SetPixel(cx + d, cy + d, r, g, b)  # SE

        # Panel frame  (ix+1 … ix+30,  iy+17 … iy+30)
        px, py, pw, ph = ix + 1, iy + 17, 29, 13
        graphics.DrawLine(canvas, px,      py,      px + pw, py,      c)
        graphics.DrawLine(canvas, px,      py + ph, px + pw, py + ph, c)
        graphics.DrawLine(canvas, px,      py,      px,      py + ph, c)
        graphics.DrawLine(canvas, px + pw, py,      px + pw, py + ph, c)
        # 3 columns
        graphics.DrawLine(canvas, px + 10, py, px + 10, py + ph, c)
        graphics.DrawLine(canvas, px + 20, py, px + 20, py + ph, c)
        # 2 rows
        graphics.DrawLine(canvas, px, py + 6, px + pw, py + 6, c)

    def _home_icon(self, canvas, graphics, ix, iy):
        c = self.home_c

        # Roof (peak at ix+15, iy+1 — eave at iy+13)
        graphics.DrawLine(canvas, ix + 15, iy + 1,  ix + 1,  iy + 13, c)
        graphics.DrawLine(canvas, ix + 15, iy + 1,  ix + 29, iy + 13, c)
        graphics.DrawLine(canvas, ix + 1,  iy + 13, ix + 29, iy + 13, c)

        # Walls + floor
        graphics.DrawLine(canvas, ix + 3,  iy + 13, ix + 3,  iy + 30, c)
        graphics.DrawLine(canvas, ix + 28, iy + 13, ix + 28, iy + 30, c)
        graphics.DrawLine(canvas, ix + 3,  iy + 30, ix + 28, iy + 30, c)

        # Door
        graphics.DrawLine(canvas, ix + 11, iy + 30, ix + 11, iy + 21, c)
        graphics.DrawLine(canvas, ix + 19, iy + 30, ix + 19, iy + 21, c)
        graphics.DrawLine(canvas, ix + 11, iy + 21, ix + 19, iy + 21, c)

        # Windows (two symmetric 4×3 outlines)
        for wx in (ix + 5, ix + 21):
            graphics.DrawLine(canvas, wx,     iy + 16, wx + 4, iy + 16, c)
            graphics.DrawLine(canvas, wx,     iy + 19, wx + 4, iy + 19, c)
            graphics.DrawLine(canvas, wx,     iy + 16, wx,     iy + 19, c)
            graphics.DrawLine(canvas, wx + 4, iy + 16, wx + 4, iy + 19, c)

    def _battery_icon(self, canvas, graphics, ix, iy, charge_pct, is_charging, is_discharging):
        c = self.batt_c

        # Terminal nub (6px wide, centered in 16px body)
        graphics.DrawLine(canvas, ix + 13, iy + 1,  ix + 18, iy + 1,  c)
        graphics.DrawLine(canvas, ix + 13, iy + 1,  ix + 13, iy + 3,  c)
        graphics.DrawLine(canvas, ix + 18, iy + 1,  ix + 18, iy + 3,  c)

        # Body outline (16px wide, centered: ix+8 .. ix+23)
        graphics.DrawLine(canvas, ix + 8,  iy + 3,  ix + 23, iy + 3,  c)
        graphics.DrawLine(canvas, ix + 8,  iy + 31, ix + 23, iy + 31, c)
        graphics.DrawLine(canvas, ix + 8,  iy + 3,  ix + 8,  iy + 31, c)
        graphics.DrawLine(canvas, ix + 23, iy + 3,  ix + 23, iy + 31, c)

        # Fill (interior: ix+9..ix+22, iy+4..iy+30 = 27 rows)
        body_h   = 27
        fill_h   = int(round(charge_pct / 100.0 * body_h))
        fill_top = iy + 31 - fill_h

        if charge_pct > 50:
            fill_c = self.fill_high
        elif charge_pct > 25:
            fill_c = self.fill_mid
        else:
            fill_c = self.fill_low

        # Wave: sweeps up when charging, down when discharging
        if (is_charging or is_discharging) and fill_h > 0:
            if is_charging:
                wave_row = iy + 30 - (self._phase // 3 % fill_h)
            else:
                wave_row = fill_top + (self._phase // 3 % fill_h)
        else:
            wave_row = -1

        for row in range(fill_top, iy + 31):
            row_c = self.wave_c if row == wave_row else fill_c
            graphics.DrawLine(canvas, ix + 9, row, ix + 22, row, row_c)

        # Battery frame PNG overlaid on top of fill (transparent interior lets fill show through)
        if self._batt_frame_png:
            self._draw_png(canvas, ix, iy, self._batt_frame_png)

        # Arrow on top of fill
        mx = ix + 15
        ac = self.arrow_c
        if is_charging:
            graphics.DrawLine(canvas, mx,     iy + 12, mx,     iy + 24, ac)  # stem
            graphics.DrawLine(canvas, mx - 4, iy + 13, mx,     iy + 8,  ac)  # left head
            graphics.DrawLine(canvas, mx + 4, iy + 13, mx,     iy + 8,  ac)  # right head
        elif is_discharging:
            graphics.DrawLine(canvas, mx,     iy + 8,  mx,     iy + 20, ac)  # stem
            graphics.DrawLine(canvas, mx - 4, iy + 19, mx,     iy + 24, ac)  # left head
            graphics.DrawLine(canvas, mx + 4, iy + 19, mx,     iy + 24, ac)  # right head

    def _grid_icon(self, canvas, graphics, ix, iy):
        c = self.grid_c
        w = 5  # bolt stroke width

        # Upper bolt: rows iy+1..iy+15, slides from right (col 20) to left (col 13)
        for dy in range(15):
            left = round(ix + 20 - dy * 7 / 14)
            graphics.DrawLine(canvas, left, iy + 1 + dy, left + w, iy + 1 + dy, c)

        # Bridge: rows iy+16..iy+17
        graphics.DrawLine(canvas, ix + 13, iy + 16, ix + 25, iy + 16, c)
        graphics.DrawLine(canvas, ix + 13, iy + 17, ix + 25, iy + 17, c)

        # Lower bolt: rows iy+18..iy+31, slides from right (col 18) to left (col 9)
        for dy in range(14):
            left = round(ix + 18 - dy * 9 / 13)
            graphics.DrawLine(canvas, left, iy + 18 + dy, left + w, iy + 18 + dy, c)

    # ── PNG icon rendering ─────────────────────────────────────────────────────

    def _draw_png(self, canvas, ix, iy, img) -> None:
        for x in range(img.width):
            for y in range(img.height):
                r, g, b, a = img.getpixel((x, y))
                if a > 0:
                    canvas.SetPixel(ix + x, iy + y, r, g, b)

    # ── Flow helpers ───────────────────────────────────────────────────────────

    def _flow(self, canvas, x_start, width, y, color, rightward):
        r, g, b = color.red, color.green, color.blue
        # 4 dots × spacing 4 = 16 (== width), so wrap gap equals every other gap
        DOT_SZ  = 2
        SPACING = 4
        N_DOTS  = width // SPACING  # stays correct if width ever changes
        for dot in range(N_DOTS):
            pos = (self._phase // 2 + dot * SPACING) % width
            px  = x_start + pos if rightward else x_start + width - 1 - pos
            for dx in range(DOT_SZ):
                ax = px + (dx if rightward else -dx)
                if x_start <= ax < x_start + width:
                    for dy in (-1, 0, 1):
                        canvas.SetPixel(ax, y + dy, r, g, b)

    def _flow_idle(self, canvas, x_start, width, y, color):
        r, g, b = color.red, color.green, color.blue
        # Match idle dot positions to the animated spacing (every 4px)
        for pos in range(1, width, 4):
            for dy in (-1, 0, 1):
                canvas.SetPixel(x_start + pos, y + dy, r, g, b)

    # ── Value text ─────────────────────────────────────────────────────────────

    def _value(self, canvas, graphics, center_x, text, color):
        char_w = self._font["size"]["width"]
        x = center_text_position(text, center_x, char_w)
        graphics.DrawText(canvas, self._font["font"], x, _VALUE_Y, color, text)

    def _small_value(self, canvas, graphics, center_x, text, color):
        char_w = self._small_font["size"]["width"]
        x = center_text_position(text, center_x, char_w)
        graphics.DrawText(canvas, self._small_font["font"], x, _BATT_KW_Y, color, text)
