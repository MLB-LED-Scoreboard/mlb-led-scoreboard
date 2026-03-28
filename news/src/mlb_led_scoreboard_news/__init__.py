from .config import Config
from .data import NewsData
from .renderer import Renderer


def load() -> tuple[type[Config], type[NewsData], type[Renderer]]:
    return Config, NewsData, Renderer
