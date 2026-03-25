import abc
from typing import TYPE_CHECKING


from .data import PluginData
from .config import Config, Layout, Color

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas
    from RGBMatrixEmulator import graphics


class Renderer(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config: Config, layout: Layout, colors: Color, scrolling_speed: float) -> None: ...

    @abc.abstractmethod
    def wait_time(self) -> float: ...

    @abc.abstractmethod
    def render(self, data: PluginData, canvas: "Canvas", graphics: "graphics", scrolling_text_pos: int) -> int: ...
