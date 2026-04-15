"""
Adapter for the hzeller rpi-rgb-led-matrix library.
This wraps the existing rgbmatrix library to conform to our base interface.
Compatible with Raspberry Pi 4 and earlier.
"""

from driver.base import MatrixDriverBase, GraphicsBase


class HzellerMatrixAdapter(MatrixDriverBase):
    """Adapter for the hzeller rgbmatrix library."""

    def __init__(self, options):
        """Initialize using the rgbmatrix library."""
        import rgbmatrix
        self._matrix = rgbmatrix.RGBMatrix(options=options)
        self._rgbmatrix = rgbmatrix

    @property
    def width(self):
        return self._matrix.width

    @property
    def height(self):
        return self._matrix.height

    def CreateFrameCanvas(self):
        return self._matrix.CreateFrameCanvas()

    def SwapOnVSync(self, canvas):
        return self._matrix.SwapOnVSync(canvas)

    def SetImage(self, image, offset_x=0, offset_y=0):
        return self._matrix.SetImage(image, offset_x, offset_y)

    def Clear(self):
        return self._matrix.Clear()


class HzellerGraphicsAdapter(GraphicsBase):
    """Adapter for hzeller graphics module."""

    def __init__(self):
        from rgbmatrix import graphics
        self._graphics = graphics

    def DrawText(self, canvas, font, x, y, color, text):
        return self._graphics.DrawText(canvas, font, x, y, color, text)

    def DrawLine(self, canvas, x1, y1, x2, y2, color):
        return self._graphics.DrawLine(canvas, x1, y1, x2, y2, color)

    def Color(self, r, g, b):
        return self._graphics.Color(r, g, b)

    def Font(self):
        return self._graphics.Font()
