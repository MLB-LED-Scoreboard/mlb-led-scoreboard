"""
Base interface for matrix drivers.
This defines the common interface that both hzeller and PioMatter adapters must implement.
"""

from abc import ABC, abstractmethod
from typing import Tuple


class MatrixDriverBase(ABC):
    """Abstract base class for matrix drivers."""

    @abstractmethod
    def __init__(self, options):
        """Initialize the matrix with the given options."""
        pass

    @property
    @abstractmethod
    def width(self) -> int:
        """Get the width of the matrix."""
        pass

    @property
    @abstractmethod
    def height(self) -> int:
        """Get the height of the matrix."""
        pass

    @abstractmethod
    def CreateFrameCanvas(self):
        """Create a new frame canvas for double-buffering."""
        pass

    @abstractmethod
    def SwapOnVSync(self, canvas):
        """Swap the given canvas with the displayed canvas."""
        pass

    @abstractmethod
    def SetImage(self, image, offset_x=0, offset_y=0):
        """Set an image on the matrix."""
        pass

    @abstractmethod
    def Clear(self):
        """Clear the matrix."""
        pass


class GraphicsBase(ABC):
    """Abstract base class for graphics operations."""

    @abstractmethod
    def DrawText(self, canvas, font, x, y, color, text):
        """Draw text on the canvas."""
        pass

    @abstractmethod
    def DrawLine(self, canvas, x1, y1, x2, y2, color):
        """Draw a line on the canvas."""
        pass

    @abstractmethod
    def Color(self, r, g, b):
        """Create a color object."""
        pass

    @abstractmethod
    def Font(self):
        """Create a font object."""
        pass
