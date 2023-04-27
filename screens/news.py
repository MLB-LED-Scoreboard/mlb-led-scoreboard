from screens.base import MLBLEDScoreboardScreen
from driver import graphics
from renderers import scrollingtext
from utils import center_text_position

import PIL, time

class NewsScreen(MLBLEDScoreboardScreen):


    class ScrollConfig:
        def __init__(self, coords, color, bgcolor, font):
            self.coords = coords
            self.color = graphics.Color(color["r"], color["g"], color["b"])
            self.bgcolor = graphics.Color(bgcolor["r"], bgcolor["g"], bgcolor["b"])
            self.font = font


    def on_render(self):
        self.canvas.Fill(
            self.background_color["r"],
            self.background_color["g"],
            self.background_color["b"]
        )

        self.__render_ticker()
        self.__render_clock()
        self.__render_weather()

        self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def __render_ticker(self):
        remaining_length = scrollingtext.render_text(
            self.canvas,
            self.scroll_config.coords["x"],
            self.scroll_config.coords["y"],
            self.scroll_config.coords["width"],
            self.scroll_config.font,
            self.scroll_config.color,
            self.scroll_config.bgcolor,
            self.headline_text,
            self.scroll_position
        )

        self.update_scroll_position(remaining_length, self.canvas.width)

    def __render_clock(self):
        time_format = "{}:%M".format(self.data.config.time_format)
        if self.data.config.time_format == "%I":
            time_format += "%p"

        time_str = time.strftime(time_format)
        coords = self.data.config.layout.coords("offday.time")
        font = self.data.config.layout.font("offday.time")
        color = self.data.config.scoreboard_colors.graphics_color("offday.time")
        position = center_text_position(time_str, coords["x"], font["size"]["width"])

        graphics.DrawText(self.canvas, font["font"], position, coords["y"], color, time_str)

    def __render_weather(self):
        if self.weather.available():
            image_path = self.weather.icon_filename()
            weather_icon = PIL.Image.open(image_path)
            self.__render_weather_icon(weather_icon)
            self.__render_weather_text(self.weather.conditions, "conditions")
            self.__render_weather_text(self.weather.temperature_string(), "temperature")
            self.__render_weather_text(self.weather.wind_speed_string(), "wind_speed")
            self.__render_weather_text(self.weather.wind_dir_string(), "wind_dir")
            self.__render_weather_text(self.weather.wind_string(), "wind")

    def __render_weather_text(self, text, keyname):
        coords = self.data.config.layout.coords("offday.{}".format(keyname))
        font = self.data.config.layout.font("offday.{}".format(keyname))
        color = self.data.config.scoreboard_colors.color.graphics_color("offday.{}".format(keyname))
        text_x = center_text_position(text, coords["x"], font["size"]["width"])

        graphics.DrawText(self.canvas, font["font"], text_x, coords["y"], color, text)

    @property
    def weather(self):
        return self.data.weather

    @property
    def scroll_config(self):
        if not hasattr(self, "_scroll_config"):
            self._scroll_config = NewsScreen.ScrollConfig(
                self.data.config.layout.coords("offday.scrolling_text"),
                self.data.config.scoreboard_colors.color("offday.scrolling_text"),
                self.data.config.scoreboard_colors.color("default.background"),
                self.data.config.layout.font("offday.scrolling_text")
            )
        
        return self._scroll_config

    @property
    def headline_text(self):
        return self.data.headlines.ticker_string()
