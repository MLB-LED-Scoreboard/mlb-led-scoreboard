from importlib.metadata import entry_points
from typing import Callable

from bullpen import PLUGIN_GROUP, api

from data.config import Config
from bullpen.logging import LOGGER


def load_plugins(config: Config) -> dict[str, tuple[api.PluginData, api.PluginRenderer]]:

    plugins = {}
    discovered_plugins = entry_points(group=PLUGIN_GROUP)
    for entry_point in discovered_plugins:
        name = entry_point.name
        if name in plugins:
            raise ValueError(f"Duplicate plugin name detected: {name} from {entry_point.module}")
        try:
            plugin: Callable[[], api.PLUGIN_DEFINITION] = entry_point.load()
            cfg_class, data_class, renderer_class = plugin()
            cfg = cfg_class(config.for_plugin(name))
            data = data_class(cfg)
            renderer = renderer_class(cfg, config.layout.for_plugin(name), config.scoreboard_colors.for_plugin(name))
        except Exception as e:
            raise ValueError(f"Error loading plugin {name} from {entry_point.module}") from e

        plugins[name] = (data, renderer)

    plugin_names = list(plugins.keys()) + ["news"]
    LOGGER.info("Loaded plugins: %s", ", ".join(plugin_names))
    config.check_screens(plugin_names)
    return plugins
