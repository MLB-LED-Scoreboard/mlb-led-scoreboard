from driver import graphics


def DrawRect(canvas, x, y, width, height, color, filled=True):
    if filled:
        _DrawFilledRect(canvas, x, y, width, height, color)
    else:
        _DrawUnfilledRect(canvas, x, y, width, height, color)

def _DrawFilledRect(canvas, x, y, width, height, color):
    """
    Draws a rectangle on screen with (X, Y) given as screen coordinates where (0, 0) is top left.

    Chooses the smallest dimension as the render direction to prevent extra draw calls.
    """
    if width > height:
        for offset in range(0, height):
            graphics.DrawLine(canvas, x, y + offset, x + width - 1, y + offset, color)
    else:
        for offset in range(0, width):
            graphics.DrawLine(canvas, x + offset, y, x + offset, y + height - 1, color)

def _DrawUnfilledRect(canvas, x, y, width, height, color):
    # Top horizontal
    graphics.DrawLine(canvas, x, y, x + width, y, color)
    # Bottom horizontal
    graphics.DrawLine(canvas, x, y + height, x + width, y + height, color)
    # Left vertical
    graphics.DrawLine(canvas, x, y, x, y + height, color)
    # Right vertical
    graphics.DrawLine(canvas, x + width, y, x + width, y + height, color)
   