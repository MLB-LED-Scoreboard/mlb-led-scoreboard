from utils import logger as ScoreboardLogger

from data.screen_request import ScreenRequest

from screens import Screen
from screens.static import StaticScreen
from screens.clock import ClockScreen
from screens.weather import WeatherScreen
from screens.games.pregame import PregameScreen
from screens.games.live_game import LiveGameScreen
from screens.games.postgame import PostgameScreen


class ScreenManager:
    SCREENS = {
        Screen.STATIC: StaticScreen,
        Screen.CLOCK: ClockScreen,
        Screen.WEATHER: WeatherScreen,
        Screen.PREGAME: PregameScreen,
        Screen.LIVE_GAME: LiveGameScreen,
        Screen.POSTGAME: PostgameScreen,
    }

    def __init__(self, matrix, canvas, config, queue):
        self.matrix = matrix
        self.canvas = canvas
        self.config = config
        self.data = None
        self.queue = queue
        self.screen = StaticScreen(self)

    def start(self):
        while True:
            if not self.queue.empty():
                self.__handle_screen_request()

            self.screen._render()

            self.canvas = self.matrix.SwapOnVSync(self.canvas)

    def request_next_screen(self, screen, **kwargs):
        request = ScreenRequest(screen, self, **kwargs)

        self.queue.put(request)

    def connect_datasource(self, data):
        self.data = data

    def __handle_screen_request(self):
        request = self.queue.get()

        if not isinstance(request, ScreenRequest):
            ScoreboardLogger.warning(
                f"Screen manager received transition request for instance of {type(request)}, but must be a ScreenRequest"
            )

            return False

        screen_class = ScreenManager.SCREENS.get(request.type, None)

        if not screen_class:
            ScoreboardLogger.warning(
                f"Screen manager received transition request for screen type of {request.type}, but no such screen type exists"
            )

            return False

        try:
            screen = screen_class(request.manager, **request.kwargs)
        except Exception as exception:
            ScoreboardLogger.exception(exception)
            ScoreboardLogger.exception("Screen manager failed to process screen transition!")

            return False

        # If not ready to transition, re-queue the request for later.
        if not self.screen.ready_to_transition():
            self.queue.put(request)

            return False

        self.__perform_transition(screen)

        return True

    def __perform_transition(self, screen):
        self.screen = screen

        # TODO: This could be an animated transition of some kind
        self.canvas.Clear()
