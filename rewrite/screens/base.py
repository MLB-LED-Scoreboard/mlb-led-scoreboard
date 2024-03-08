from datetime import datetime as dt

class ScreenBase():

    def __init__(self, manager):
        self._manager = manager

        self.start_time = None
        self.duration = 0

    def request_next_screen(self, screen):
        self._manager.queue.put(screen)
    
    def track_duration(fn):
        def wrapper(self, *args, **kwargs):
            if self.start_time is None:
                self.start_time = dt.now()

            fn(self, *args, **kwargs)

            self.duration = (dt.now() - self.start_time).total_seconds() * 1000

        return wrapper

    def render(self):
        raise NotImplementedError("Subclasses must implement render()")
    
    @track_duration
    def _render(self):
        self.render()
    
    @property
    def matrix(self):
        return self._manager.matrix

    @property
    def canvas(self):
        return self._manager.canvas
