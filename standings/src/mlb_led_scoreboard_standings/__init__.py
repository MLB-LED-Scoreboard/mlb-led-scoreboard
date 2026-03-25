from .config import Config
from .standings import Standings
from .renderer import Renderer


def load() -> tuple[type[Config], type[Standings], type[Renderer]]:
    return Config, Standings, Renderer
