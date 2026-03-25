import abc
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from RGBMatrixEmulator.graphics import Color


class Config(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config_json: Union[Any, dict[str, Any]]) -> None: ...


class Layout(abc.ABC):
    @abc.abstractmethod
    def font(self, keypath: str) -> dict[str, Any]: ...

    @abc.abstractmethod
    def coords(self, keypath: str) -> Union[Any, dict[str, Any]]: ...


class Color(abc.ABC):
    @abc.abstractmethod
    def color(self, keypath: str) -> dict[str, int]: ...

    @abc.abstractmethod
    def graphics_color(self, keypath: str) -> "Color": ...
