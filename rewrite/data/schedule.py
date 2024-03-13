import statsapi, time

from datetime import datetime as dt

from utils import logger as ScoreboardLogger

from data.update_status import UpdateStatus
from data.game import Game

from screens import Screen


class Schedule:
    REFRESH_RATE = 5 * 60  # minutes

    def __init__(self, data):
        self.data = data

        # Contains a list of parsed game objects
        self.games = []
        # Cached request from statsapi
        self._games = []

        self.game = None

        self.update()

    def update(self):
        self.last_update = time.time()

        ScoreboardLogger.log(f"Updating schedule for {dt.today()}")

        try:
            self.__fetch_updated_schedule(dt.today())
        except Exception as exception:
            ScoreboardLogger.exception("Networking error while refreshing schedule!")
            ScoreboardLogger.exception(exception)

            return UpdateStatus.FAIL

        # TODO: Filter to target game
        self.game = self.games[0]

        self.__request_transition_to_game(self.game)

        return UpdateStatus.SUCCESS

    def request_next_game(self):
        self.game = self.games[self.__next_game_index()]

        self.__request_transition_to_game(self.game)

    def __fetch_updated_schedule(self, date):
        # self._games = statsapi.schedule(date.strftime("%Y-%m-%d"))
        self._games = statsapi.schedule(date.strftime("2024-03-12"))

        self.games = [Game.from_schedule(game) for game in self._games]

    def __request_transition_to_game(self, game):
        next_screen = None

        if game.is_complete():
            next_screen = Screen.POSTGAME
        elif game.is_pregame():
            next_screen = Screen.PREGAME
        elif game.is_live():
            next_screen = Screen.LIVE_GAME

        if next_screen is not None:
            game.update(True)
            self.data.request_next_screen(next_screen, game=game)

    def __next_game_index(self):
        if len(self.games) > 0 and self.game in self.games:
            i = self.games.index(self.game)

            return (i + 1) % len(self.games)

        return 0
