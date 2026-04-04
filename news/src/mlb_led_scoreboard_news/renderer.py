from typing import TYPE_CHECKING


import time

from PIL import Image

import bullpen.api as api
from bullpen.time_formats import TIME_FORMAT_12H
from bullpen.util import center_text_position, scrolling_text

from .config import Config
from .weather import Weather
from .headlines import Headlines
from .data import NewsData

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas


class Renderer(api.PluginRenderer["NewsData"]):
    def __init__(self, config: Config, layout: api.Layout, colors: api.Color):
        self.config = config
        self.layout = layout
        self.colors = colors

        self.bg = colors.graphics_color("default.background")

        time_format = config.time_format
        self.time_fmt_str = "{}:%M".format(time_format)
        if time_format == TIME_FORMAT_12H:
            self.time_fmt_str += "%p"
        self.time_coords = layout.coords("offday.time")
        self.time_font = layout.font("offday.time")
        self.time_color = colors.graphics_color("offday.time")

        self.scroll_coords = layout.coords("offday.scrolling_text")
        self.scroll_font = layout.font("offday.scrolling_text")
        self.scroll_color = colors.graphics_color("offday.scrolling_text")

        self.icon_coords = layout.coords("offday.weather_icon")
        self.icon_color = colors.color("offday.weather_icon")

        self.first = True

    def wait_time(self) -> float:
        return self.config.scrolling_speed

    def render(self, data: NewsData, canvas: "Canvas", graphics: api.renderer.graphics, scrolling_text_pos: int) -> int:
        if scrolling_text_pos == canvas.width:
            if self.first:
                self.first = False
            else:
                data.headlines.advance_ticker()

        canvas.Fill(self.bg.red, self.bg.green, self.bg.blue)

        text_len = self._render_news_ticker(canvas, graphics, data.headlines, scrolling_text_pos)
        self._render_clock(canvas, graphics)
        self._render_weather(canvas, graphics, self.layout, self.colors, data.weather)

        return text_len

    def _render_clock(self, canvas, graphics):

        time_text = time.strftime(self.time_fmt_str)

        text_x = center_text_position(time_text, self.time_coords["x"], self.time_font["size"]["width"])
        graphics.DrawText(canvas, self.time_font["font"], text_x, self.time_coords["y"], self.time_color, time_text)

    def _render_weather(self, canvas, graphics, layout, colors, weather: Weather):
        if weather.available():
            self._render_weather_icon(canvas, weather.icon())
            _render_weather_text(canvas, graphics, layout, colors, weather.conditions, "conditions")
            _render_weather_text(canvas, graphics, layout, colors, weather.temperature_string(), "temperature")
            _render_weather_text(canvas, graphics, layout, colors, weather.wind_speed_string(), "wind_speed")
            _render_weather_text(canvas, graphics, layout, colors, weather.wind_dir_string(), "wind_dir")
            _render_weather_text(canvas, graphics, layout, colors, weather.wind_string(), "wind")

    def _render_weather_icon(self, canvas, weather_icon):

        resize = self.icon_coords.get("rescale_icon")

        if resize:
            weather_icon = weather_icon.resize(
                (weather_icon.width * resize, weather_icon.height * resize), Image.NEAREST
            )
        for x in range(weather_icon.width):
            for y in range(weather_icon.height):
                pixel = weather_icon.getpixel((x, y))
                if pixel[3] > 0:
                    canvas.SetPixel(
                        self.icon_coords["x"] + x,
                        self.icon_coords["y"] + y,
                        self.icon_color["r"],
                        self.icon_color["g"],
                        self.icon_color["b"],
                    )

    def _render_news_ticker(self, canvas: "Canvas", graphics, headlines: Headlines, text_pos) -> int:

        ticker_text = headlines.ticker_string()
        return scrolling_text(
            canvas,
            graphics,
            self.scroll_coords["x"],
            self.scroll_coords["y"],
            self.scroll_coords["width"],
            self.scroll_font,
            self.scroll_color,
            self.bg,
            ticker_text,
            text_pos,
            force_scroll=True,
        )


def _render_weather_text(canvas, graphics, layout, colors, text, keyname):
    coords = layout.coords("offday.{}".format(keyname))
    font = layout.font("offday.{}".format(keyname))
    color = colors.graphics_color("offday.{}".format(keyname))
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)
