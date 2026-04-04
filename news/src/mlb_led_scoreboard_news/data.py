from bullpen.api import UpdateStatus, PluginData

from .config import Config
from .weather import Weather
from .headlines import Headlines


class NewsData(PluginData):

    def __init__(self, config: Config):
        # Weather info
        self.weather: Weather = Weather(config)

        # News headlines
        self.headlines: Headlines = Headlines(config)

    def update(self, force=False) -> UpdateStatus:
        return UpdateStatus.merge([self.weather.update(force), self.headlines.update(force)])
