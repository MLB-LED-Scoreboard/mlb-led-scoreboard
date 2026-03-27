from typing import Any, Callable
import debug


class DoubleBuffer:
    """
    This class is used to coordinate data that is fetched on the main thread but
    draw on the render thread (currently, games).

    Essentially, we need two properties upheld:
    - The game currently rendering on the render thread can still be
      accessed from the main thread (e.g. so that we can call .update() on it)
    - The render thread can switch to the next game when it pleases, and a populated
      game will be waiting for it.

    The result is something kind of like a double buffer from computer graphics.
    """

    def __init__(self, initial_data) -> None:
        self.items = (initial_data, initial_data)
        self._reading_next = False

    def next(self):
        """
        Called on the render thread when it wants the next game to render.
        """
        debug.log("Render thread: reading 'next'")
        self._reading_next = True
        return self.items[1]

    def producer_tick(self, getter: Callable[[Any], Any]):
        """
        Called periodically on the main thread.
        If the render thread has moved on, this copies 'next' into 'current' on one tick,
        then updates 'next' with new data from `getter` on the next tick.
        """
        if not self._reading_next and (self.items[0] == self.items[1]):
            next = getter(self.items[1])
            if next is not None and next != self.items[1]:
                debug.log("Main thread: replacing 'next' with new data")
                self.items = (self.items[0], next)

        if self._reading_next:
            debug.log("Main thread: mirroring 'next' into 'current'")
            self.items = (self.items[1], self.items[1])
            self._reading_next = False
