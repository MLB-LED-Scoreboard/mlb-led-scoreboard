from bullpen.api import PluginData
import bullpen.api.update

from .config import Config
from .weather import Weather
from .headlines import Headlines


class NewsData(PluginData):

    def __init__(self, config: Config):
        # Weather info
        self.weather: Weather = Weather(config)

        # News headlines
        self.headlines: Headlines = Headlines(config)

    def update(self, force=False) -> bullpen.api.update.UpdateStatus:
        return bullpen.api.update.merge([self.weather.update(force), self.headlines.update(force)])
