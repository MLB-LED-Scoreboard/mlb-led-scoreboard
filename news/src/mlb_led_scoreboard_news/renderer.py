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


class Renderer(api.Renderer):
    def __init__(self, config: Config, layout: api.Layout, colors: api.Color):
        self.config = config
        self.layout = layout
        self.colors = colors

        self.first = True

    def wait_time(self) -> float:
        return self.config.scrolling_speed

    def render(self, data: NewsData, canvas: "Canvas", graphics: api.renderer.graphics, scrolling_text_pos: int) -> int:
        if scrolling_text_pos == canvas.width:
            if self.first:
                self.first = False
            else:
                data.headlines.advance_ticker()

        color = self.colors.color("default.background")
        canvas.Fill(color["r"], color["g"], color["b"])

        pos = render_offday_screen(
            canvas,
            graphics,
            self.layout,
            self.colors,
            data.weather,
            data.headlines,
            self.config.time_format,
            scrolling_text_pos,
        )
        return pos


def render_offday_screen(
    canvas,
    graphics,
    layout: api.Layout,
    colors: api.Color,
    weather: Weather,
    headlines: Headlines,
    time_format,
    text_pos,
):
    text_len = _render_news_ticker(canvas, graphics, layout, colors, headlines, text_pos)
    _render_clock(canvas, graphics, layout, colors, time_format)
    _render_weather(canvas, graphics, layout, colors, weather)

    return text_len


def _render_clock(canvas, graphics, layout, colors, time_format):
    time_format_str = "{}:%M".format(time_format)
    if time_format == TIME_FORMAT_12H:
        time_format_str += "%p"
    time_text = time.strftime(time_format_str)
    coords = layout.coords("offday.time")
    font = layout.font("offday.time")
    color = colors.graphics_color("offday.time")
    text_x = center_text_position(time_text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, time_text)


def _render_weather(canvas, graphics, layout, colors, weather):
    if weather.available():
        _render_weather_icon(canvas, layout, colors, weather.icon())
        _render_weather_text(canvas, graphics, layout, colors, weather.conditions, "conditions")
        _render_weather_text(canvas, graphics, layout, colors, weather.temperature_string(), "temperature")
        _render_weather_text(canvas, graphics, layout, colors, weather.wind_speed_string(), "wind_speed")
        _render_weather_text(canvas, graphics, layout, colors, weather.wind_dir_string(), "wind_dir")
        _render_weather_text(canvas, graphics, layout, colors, weather.wind_string(), "wind")


def _render_weather_text(canvas, graphics, layout, colors, text, keyname):
    coords = layout.coords("offday.{}".format(keyname))
    font = layout.font("offday.{}".format(keyname))
    color = colors.graphics_color("offday.{}".format(keyname))
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)


def _render_weather_icon(canvas, layout, colors, weather_icon):
    coords = layout.coords("offday.weather_icon")
    color = colors.color("offday.weather_icon")
    resize = coords.get("rescale_icon")

    if resize:
        weather_icon = weather_icon.resize((weather_icon.width * resize, weather_icon.height * resize), Image.NEAREST)
    for x in range(weather_icon.width):
        for y in range(weather_icon.height):
            pixel = weather_icon.getpixel((x, y))
            if pixel[3] > 0:
                canvas.SetPixel(coords["x"] + x, coords["y"] + y, color["r"], color["g"], color["b"])


def _render_news_ticker(canvas, graphics, layout, colors, headlines, text_pos):
    coords = layout.coords("offday.scrolling_text")
    font = layout.font("offday.scrolling_text")
    color = colors.graphics_color("offday.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    ticker_text = headlines.ticker_string()
    return scrolling_text(
        canvas,
        graphics,
        coords["x"],
        coords["y"],
        coords["width"],
        font,
        color,
        bgcolor,
        ticker_text,
        text_pos,
        force_scroll=True,
    )
