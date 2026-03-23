from typing import Any, Callable, Literal
import debug


class DoubleBuffer:
    def __init__(self, initial_data) -> None:
        self.items = (initial_data, initial_data)
        # render thread can switch to next
        self._active: Literal["current", "next"] = "current"

    def active(self):
        debug.log("Render thread: reading '%s'", self._active)
        if self._active == "current":
            return self.items[0]
        else:
            return self.items[1]

    def consumer_advance(self):
        if self._active == "current":
            debug.log("Render thread: informing main thread that render thread will read 'next' ")
        self._active = "next"

    def producer_tick(self, getter: Callable[[Any], Any]):
        if self._active == "current" and (self.items[0] == self.items[1]):
            self.items = (self.items[0], getter(self.items[1]))
            debug.log("Main thread: advanced 'next' game")

        if self._active == "next":
            debug.log("Main thread: acknowledging render thread's request to read 'next', mirroring into 'current'")
            self.items = (self.items[1], self.items[1])
            self._active = "current"
            debug.log("Main thread: resetting active to 'current'")
