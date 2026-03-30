import abc
from typing import TYPE_CHECKING, Optional, Protocol


from .data import PluginData
from .config import PluginConfig, Layout, Color

if TYPE_CHECKING:
    from RGBMatrixEmulator.emulation.canvas import Canvas
    from RGBMatrixEmulator import Color as GraphicsColor, Font


class graphics(Protocol):
    def DrawText(self, canvas: "Canvas", font: "Font", x: int, y: int, color: "GraphicsColor", text: str) -> int: ...

    def DrawLine(self, canvas: "Canvas", x1: int, y1: int, x2: int, y2: int, color: "GraphicsColor") -> None: ...

    def DrawCircle(self, canvas: "Canvas", x: int, y: int, r: int, color: "GraphicsColor") -> None: ...


class PluginRenderer(abc.ABC):
    @abc.abstractmethod
    def __init__(self, config: PluginConfig, layout: Layout, colors: Color) -> None: ...

    @abc.abstractmethod
    def wait_time(self) -> float: ...

    @abc.abstractmethod
    def render(
        self, data: PluginData, canvas: "Canvas", graphics: graphics, scrolling_text_pos: int
    ) -> Optional[int]: ...

    def reset(self):
        """Called at the end of rendering, can be used to reset state before switching off"""
        pass

    def can_render(self, data: PluginData) -> bool:
        return True
