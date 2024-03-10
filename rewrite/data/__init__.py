from data.schedule import Schedule

from data.screen_request import ScreenRequest


class Data:

    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

        self.schedule = Schedule(self)

    def request_next_screen(self, screen):
        self.screen_manager.request_next_screen(screen, self)
