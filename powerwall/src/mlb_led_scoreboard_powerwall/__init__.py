from bullpen import api

from .config import Config
from .data import PowerwallData
from .renderer import Renderer


def load() -> api.PLUGIN_DEFINITION:
    return Config, PowerwallData, Renderer
