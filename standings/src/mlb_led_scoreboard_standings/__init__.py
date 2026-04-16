from bullpen import api

from .config import Config
from .standings import Standings
from .renderer import Renderer


def load() -> api.PLUGIN_DEFINITION:
    return Config, Standings, Renderer
