from data.schedule import Schedule


class Data:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

        self.schedule = Schedule(self)

    def request_next_screen(self, screen, **kwargs):
        self.screen_manager.request_next_screen(screen, **kwargs)

    @property
    def config(self):
        return self.screen_manager.config
