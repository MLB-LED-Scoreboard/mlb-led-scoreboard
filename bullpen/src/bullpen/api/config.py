import abc
import datetime
from typing import TYPE_CHECKING, Any, Protocol, Union

if TYPE_CHECKING:
    from RGBMatrixEmulator.graphics import Color as GraphicsColor


class MLBConfig(Protocol):
    scrolling_speed: float
    time_format: str
    debug: bool

    @abc.abstractmethod
    def for_plugin(self, plugin_name: str) -> dict[str, Any]: ...

    @abc.abstractmethod
    def parse_today(self) -> datetime.date: ...


class Config(abc.ABC):
    @abc.abstractmethod
    def __init__(self, base: MLBConfig) -> None: ...


class Layout(abc.ABC):
    @abc.abstractmethod
    def font(self, keypath: str) -> dict[str, Any]: ...

    @abc.abstractmethod
    def coords(self, keypath: str) -> Union[Any, dict[str, Any]]: ...


class Color(abc.ABC):
    @abc.abstractmethod
    def color(self, keypath: str) -> dict[str, int]: ...

    @abc.abstractmethod
    def graphics_color(self, keypath: str) -> "GraphicsColor": ...
