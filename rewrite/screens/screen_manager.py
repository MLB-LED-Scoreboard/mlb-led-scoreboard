from screens import Screen
from screens.base import ScreenBase
from screens.clock import ClockScreen
from screens.weather import WeatherScreen

class ScreenManager():

    SCREENS = {
        Screen.CLOCK: ClockScreen,
        Screen.WEATHER: WeatherScreen
    }

    @classmethod
    def start(cls, matrix, canvas, queue):
        ScreenManager(matrix, canvas, queue).__start()

    def __init__(self, matrix, canvas, queue):
        self.matrix = matrix
        self.canvas = canvas
        self.queue  = queue
        self.screen = WeatherScreen(self)
        self.priority = "normal" # TODO

    def __start(self):
        while True:
            if not self.queue.empty():
                screen = self.queue.get()
                screen_class = self.SCREENS.get(screen, None)

                if issubclass(screen_class, ScreenBase):
                    self.screen = screen_class(self)
                    # TODO: This could be a transition of some kind
                    self.canvas.Clear()

            self.screen._render()

            self.canvas = self.matrix.SwapOnVSync(self.canvas)
