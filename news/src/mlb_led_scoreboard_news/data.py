from bullpen import PluginData
import bullpen.update

from .config import Config
from .weather import Weather
from .headlines import Headlines


class NewsData(PluginData):

    def __init__(self, config: Config):
        # Weather info
        self.weather: Weather = Weather(config)

        # News headlines
        self.headlines: Headlines = Headlines(config)

    def update(self, force=False) -> bullpen.update.UpdateStatus:
        return bullpen.update.merge([self.weather.update(force), self.headlines.update(force)])
