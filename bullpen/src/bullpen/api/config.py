import abc
import datetime
from typing import TYPE_CHECKING, Any, Protocol, Union

if TYPE_CHECKING:
    from RGBMatrixEmulator.graphics import Color as GraphicsColor


class MLBConfig(Protocol):

    @property
    @abc.abstractmethod
    def scrolling_speed(self) -> float: ...

    @property
    @abc.abstractmethod
    def time_format(self) -> str: ...

    @property
    @abc.abstractmethod
    def plugin_config(self) -> dict[str, Any]: ...

    @abc.abstractmethod
    def parse_today(self) -> datetime.date: ...

    @abc.abstractmethod
    def is_postseason(self) -> bool: ...

    # TODO equivalent is_offseason?


class PluginConfig(abc.ABC):
    @abc.abstractmethod
    def __init__(self, base: MLBConfig) -> None: ...


class Layout(abc.ABC):
    width: int
    height: int

    @abc.abstractmethod
    def font(self, keypath: str) -> dict[str, Any]: ...

    @abc.abstractmethod
    def coords(self, keypath: str) -> Union[Any, dict[str, Any]]: ...


class Color(abc.ABC):
    @abc.abstractmethod
    def color(self, keypath: str) -> dict[str, int]: ...

    @abc.abstractmethod
    def graphics_color(self, keypath: str) -> "GraphicsColor": ...
