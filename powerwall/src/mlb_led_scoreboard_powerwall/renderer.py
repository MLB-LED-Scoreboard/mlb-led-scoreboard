from typing import TYPE_CHECKING, Optional

import bullpen.api as api

from .config import Config
from .data import PowerwallData

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas


class Renderer(api.PluginRenderer["PowerwallData"]):
    def __init__(self, config: Config, layout: api.Layout, colors: api.Color) -> None:
        self.config = config
        self.layout = layout
        self.colors = colors

        self.bg = colors.graphics_color("powerwall.background")

    def wait_time(self) -> float:
        return 1.0

    def render(
        self,
        data: PowerwallData,
        canvas: "Canvas",
        graphics: api.renderer.graphics,
        scrolling_text_pos: int,
    ) -> Optional[int]:
        canvas.Fill(self.bg.red, self.bg.green, self.bg.blue)

        self._draw_pair(canvas, graphics, "solar", "SOLAR", data.solar_kw, signed=False)
        self._draw_pair(canvas, graphics, "home", "HOME", data.home_kw, signed=False)
        self._draw_pair(canvas, graphics, "grid", "GRID", data.grid_kw, signed=True)
        self._draw_pair(canvas, graphics, "battery", "BATT", data.battery_kw, signed=True)

        self._draw_text(canvas, graphics, "mode", data.operation_mode)
        self._draw_text(canvas, graphics, "grid_status", data.grid_status)

        self._draw_battery_bar(canvas, graphics, data.charge_pct)
        self._draw_text(canvas, graphics, "battery_pct", f"{int(round(data.charge_pct))}%")

        return None

    def _draw_pair(self, canvas, graphics, key: str, label: str, value: float, signed: bool) -> None:
        label_coords = self.layout.coords(f"powerwall.{key}_label")
        label_font = self.layout.font(f"powerwall.{key}_label")
        label_color = self.colors.graphics_color(f"powerwall.{key}_label")
        graphics.DrawText(canvas, label_font["font"], label_coords["x"], label_coords["y"], label_color, label)

        value_coords = self.layout.coords(f"powerwall.{key}_value")
        value_font = self.layout.font(f"powerwall.{key}_value")
        value_color = self.colors.graphics_color(f"powerwall.{key}_value")
        graphics.DrawText(
            canvas, value_font["font"], value_coords["x"], value_coords["y"], value_color, _fmt_kw(value, signed)
        )

    def _draw_text(self, canvas, graphics, key: str, text: str) -> None:
        coords = self.layout.coords(f"powerwall.{key}")
        font = self.layout.font(f"powerwall.{key}")
        color = self.colors.graphics_color(f"powerwall.{key}")
        max_chars = coords.get("max_chars")
        if max_chars and len(text) > max_chars:
            text = text[:max_chars]
        graphics.DrawText(canvas, font["font"], coords["x"], coords["y"], color, text)

    def _draw_battery_bar(self, canvas, graphics, pct: float) -> None:
        coords = self.layout.coords("powerwall.battery_bar")
        bg_color = self.colors.graphics_color("powerwall.battery_bar_bg")
        fg_color = self.colors.graphics_color("powerwall.battery_bar")

        x = coords["x"]
        y = coords["y"]
        w = coords["width"]
        h = coords["height"]

        clamped_pct = max(0.0, min(100.0, pct))
        fill_w = int(round(w * clamped_pct / 100.0))

        for dy in range(h):
            graphics.DrawLine(canvas, x, y + dy, x + w - 1, y + dy, bg_color)
            if fill_w > 0:
                graphics.DrawLine(canvas, x, y + dy, x + fill_w - 1, y + dy, fg_color)


def _fmt_kw(kw: float, signed: bool) -> str:
    if signed:
        sign = "+" if kw >= 0 else "-"
        return f"{sign}{abs(kw):.1f}kW"
    return f"{kw:.1f}kW"
