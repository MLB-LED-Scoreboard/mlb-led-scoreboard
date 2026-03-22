from typing import Any, Callable, Literal
import debug


class DoubleBuffer:
    def __init__(self, initial_data) -> None:
        self.items = (initial_data, initial_data)
        # render thread can switch to next
        self._active: Literal["current", "next"] = "current"
        # main thread acknowledges, so it can switch back to current
        self._producer_acknowledged = False

    def active(self):
        if self._active == "current":
            return self.items[0]
        else:
            return self.items[1]

    def consumer_advance(self):
        if self._active == "current":
            debug.log("Render thread: requesting main thread to read 'next' game")
        self._active = "next"

    def producer_tick(self, getter: Callable[[Any], Any]):
        if self._active == "next":
            debug.log("Main thread: acknowledging render thread's request to read 'next', mirroring into 'current'")
            self.items = (self.items[1], self.items[1])
            self._producer_acknowledged = True

        if self._active == "current":
            if self._producer_acknowledged or (self.items[0] == self.items[1]):
                self.items = (self.items[0], getter(self.items[1]))

            if self._producer_acknowledged:
                self._producer_acknowledged = False
                debug.log("Main thread: render thread has switched back to 'current', advanced 'next' game")

    def consumer_tick(self):
        if self._active == "next" and self._producer_acknowledged:
            debug.log("Render thread: main thread has acknowledged, switching back to reading 'current' game")
            self._active = "current"
