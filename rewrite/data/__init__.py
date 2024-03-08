from data.schedule import Schedule

class Data:

    def __init__(self, screen_queue):
        self._screen_queue = screen_queue

        self.schedule = Schedule()

    def request_next_screen(self, screen):
        self._screen_queue.put(screen)
