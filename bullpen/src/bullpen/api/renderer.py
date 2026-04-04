import abc
from typing import TYPE_CHECKING, Generic, Optional, Protocol, TypeVar

from .data import PluginData
from .config import PluginConfig, Layout, Color

_PluginData = TypeVar("_PluginData", bound=PluginData)

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas
    from RGBMatrixEmulator import Color as GraphicsColor, Font


class graphics(Protocol):
    def Color(self, r=0, g=0, b=0) -> "GraphicsColor": ...

    def DrawText(self, canvas: "Canvas", font: "Font", x: int, y: int, color: "GraphicsColor", text: str) -> int: ...

    def DrawLine(self, canvas: "Canvas", x1: int, y1: int, x2: int, y2: int, color: "GraphicsColor") -> None: ...

    def DrawCircle(self, canvas: "Canvas", x: int, y: int, r: int, color: "GraphicsColor") -> None: ...


class PluginRenderer(abc.ABC, Generic[_PluginData]):
    @abc.abstractmethod
    def __init__(self, config: PluginConfig, layout: Layout, colors: Color) -> None: ...

    @abc.abstractmethod
    def wait_time(self) -> float: ...

    @abc.abstractmethod
    def render(
        self, data: _PluginData, canvas: "Canvas", graphics: graphics, scrolling_text_pos: int
    ) -> Optional[int]: ...

    def reset(self):
        """Called at the end of rendering, can be used to reset state before switching off"""
        pass

    def can_render(self, data: _PluginData) -> bool:
        return True
