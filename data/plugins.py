from importlib.metadata import entry_points
from typing import Callable, Type
import bullpen

from data.config import Config


def load_plugins(config: Config) -> list[tuple[str, bullpen.PluginData, bullpen.Renderer]]:

    plugins = []
    discovered_plugins = entry_points(group="mlbled.plugins")
    for entry_point in discovered_plugins:
        name = entry_point.name
        try:
            plugin: Callable[[], tuple[Type[bullpen.Config], Type[bullpen.PluginData], Type[bullpen.Renderer]]] = (
                entry_point.load()
            )
            cfg_class, data_class, renderer_class = plugin()
            cfg = cfg_class(config.for_plugin(name))
            data = data_class(cfg)
            renderer = renderer_class(cfg, config.layout, config.scoreboard_colors, config.scrolling_speed)
        except Exception as e:
            print(f"Error loading plugin {name}: {e}")
            continue
        plugins.append((name, data, renderer))

    return plugins
