try:
    from rgbmatrix import graphics
except ImportError:
    from RGBMatrixEmulator import graphics

import time

from PIL import Image

from data.config.color import Color
from data.config.layout import Layout
from data.headlines import Headlines
from data.weather import Weather
from renderers import scrollingtext
from utils import center_text_position, get_file


def render_offday_screen(
    canvas, layout: Layout, colors: Color, weather: Weather, headlines: Headlines, time_format, text_pos
):

    text_len = __render_news_ticker(canvas, layout, colors, headlines, text_pos)
    __render_clock(canvas, layout, colors, time_format)
    __render_weather(canvas, layout, colors, weather)

    return text_len


def __render_clock(canvas, layout, colors, time_format):
    time_format_str = "{}:%M".format(time_format)
    if time_format == "%I":
        time_format_str += "%p"
    time_text = time.strftime(time_format_str)
    coords = layout.coords("offday.time")
    font = layout.font("offday.time")
    color = colors.graphics_color("offday.time")
    text_x = center_text_position(time_text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, time_text)


def __render_weather(canvas, layout, colors, weather):
    if weather.available():
        image_file = get_file(weather.icon_filename())
        weather_icon = Image.open(image_file)
        __render_weather_icon(canvas, layout, colors, weather_icon)
        __render_weather_text(canvas, layout, colors, weather.conditions, "conditions")
        __render_weather_text(canvas, layout, colors, weather.temperature_string(), "temperature")
        __render_weather_text(canvas, layout, colors, weather.wind_speed_string(), "wind_speed")
        __render_weather_text(canvas, layout, colors, weather.wind_dir_string(), "wind_dir")
        __render_weather_text(canvas, layout, colors, weather.wind_string(), "wind")


def __render_weather_text(canvas, layout, colors, text, keyname):
    coords = layout.coords("offday.{}".format(keyname))
    font = layout.font("offday.{}".format(keyname))
    color = colors.graphics_color("offday.{}".format(keyname))
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(canvas, font["font"], text_x, coords["y"], color, text)


def __render_weather_icon(canvas, layout, colors, weather_icon):
    coords = layout.coords("offday.weather_icon")
    color = colors.color("offday.weather_icon")
    for x in range(weather_icon.size[0]):
        for y in range(weather_icon.size[1]):
            pixel = weather_icon.getpixel((x, y))
            if pixel[3] > 0:
                canvas.SetPixel(coords["x"] + x, coords["y"] + y, color["r"], color["g"], color["b"])


def __render_news_ticker(canvas, layout, colors, headlines, text_pos):
    coords = layout.coords("offday.scrolling_text")
    font = layout.font("offday.scrolling_text")
    color = colors.graphics_color("offday.scrolling_text")
    bgcolor = colors.graphics_color("default.background")
    ticker_text = headlines.ticker_string()
    return scrollingtext.render_text(
        canvas, coords["x"], coords["y"], coords["width"], font, color, bgcolor, ticker_text, text_pos
    )
