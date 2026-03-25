from importlib.metadata import entry_points
from typing import Callable, Type
import bullpen


import debug
from data.config import Config


def load_plugins(config: Config) -> dict[str, tuple[bullpen.PluginData, bullpen.Renderer]]:

    plugins = {}
    discovered_plugins = entry_points(group="mlbled.plugins")
    for entry_point in discovered_plugins:
        name = entry_point.name
        if name in plugins:
            raise ValueError(f"Duplicate plugin name detected: {name} from {entry_point.module}")
        try:
            plugin: Callable[[], tuple[Type[bullpen.Config], Type[bullpen.PluginData], Type[bullpen.Renderer]]] = (
                entry_point.load()
            )
            cfg_class, data_class, renderer_class = plugin()
            cfg = cfg_class(config)
            data = data_class(cfg)
            renderer = renderer_class(cfg, config.layout, config.scoreboard_colors)
        except Exception as e:
            raise ValueError(f"Error loading plugin {name} from {entry_point.module}") from e

        plugins[name] = (data, renderer)

    plugin_names = list(plugins.keys()) + ["news"]
    debug.info("Loaded plugins: %s", ", ".join(plugin_names))
    config.check_screens(plugin_names)
    return plugins
