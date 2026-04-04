from typing import TypeAlias

from .data import PluginData
from .renderer import PluginRenderer
from .update import UpdateStatus
from .config import PluginConfig, Layout, Color, MLBConfig


PLUGIN_DEFINITION: TypeAlias = tuple[type[PluginConfig], type[PluginData], type[PluginRenderer]]

__all__ = ["PluginData", "PluginRenderer", "UpdateStatus", "PluginConfig", "Layout", "Color", "MLBConfig"]
