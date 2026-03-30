from importlib.metadata import entry_points
from typing import Callable, Type

from . import api

from .logging import LOGGER


PLUGIN_GROUP = "bullpen.mlbled.plugin"


def load_plugins(config: api.MLBConfig) -> dict[str, tuple[api.PluginData, api.Renderer]]:

    plugins = {}
    discovered_plugins = entry_points(group=PLUGIN_GROUP)
    for entry_point in discovered_plugins:
        name = entry_point.name
        if name in plugins:
            raise ValueError(f"Duplicate plugin name detected: {name} from {entry_point.module}")
        try:
            plugin: Callable[[], tuple[Type[api.Config], Type[api.PluginData], Type[api.Renderer]]] = entry_point.load()
            cfg_class, data_class, renderer_class = plugin()
            cfg = cfg_class(config)
            data = data_class(cfg)
            renderer = renderer_class(cfg, config.layout, config.scoreboard_colors)
        except Exception as e:
            if config.debug:
                raise ValueError(f"Error loading plugin {name} from {entry_point.module}") from e
            else:
                LOGGER.warning("Error loading plugin %s from %s: %s", name, entry_point.module, str(e))

        plugins[name] = (data, renderer)

    plugin_names = list(plugins.keys()) + ["news"]
    LOGGER.info("Loaded plugins: %s", ", ".join(plugin_names))
    config.check_screens(plugin_names)
    return plugins
