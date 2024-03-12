from datetime import datetime as dt


class ScreenBase:
    def __init__(self, manager, **_kwargs):
        self.manager = manager

        self.start_time = None
        self.duration = 0

    def track_duration(fn):
        def wrapper(self, *args, **kwargs):
            if self.start_time is None:
                self.start_time = dt.now()

            fn(self, *args, **kwargs)

            self.duration = (dt.now() - self.start_time).total_seconds() * 1000

        return wrapper

    def render(self):
        raise NotImplementedError("Subclasses must implement render()")

    def ready_to_transition(self):
        """
        Returns True if the screen is ready to transition away. By default, always allow the screen to transition.

        Subclasses should implement this method if they desire different behavior, such as requiring screens to be visible for a certain duration.

        NOTE: If this value always returns False, no screen transitions will happen!
        """
        return True

    def create_cached_object(self, name, klass, *args, **kwargs):
        """
        Creates an object and caches it between render cycles. The arguments and keyword arguments are passed to the class's constructor and stored in cache under
        the configured name. Repeated calls to this function fetch from the cache instead of re-initializing.
        """
        if not hasattr(self, "_object_cache"):
            self._object_cache = {}

        if name in self._object_cache:
            return self._object_cache.get(name)

        cached_object = klass(*args, **kwargs)
        self._object_cache[name] = cached_object

        return cached_object

    @track_duration
    def _render(self):
        self.canvas.Fill(*self.background_color)
        self.render()

    @property
    def matrix(self):
        return self.manager.matrix

    @property
    def canvas(self):
        return self.manager.canvas

    @property
    def data(self):
        return self.manager.data

    @property
    def config(self):
        return self.manager.config

    @property
    def layout(self):
        return self.config.layout

    @property
    def colors(self):
        return self.config.colors

    @property
    def background_color(self):
        """
        The default background can be overridden in child classes.
        """
        return self.colors.graphics_color("default.background")

    @property
    def default_text_color(self):
        return self.colors.graphics_color("default.text")
