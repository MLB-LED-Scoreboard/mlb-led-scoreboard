import datetime, statsapi, time

from utils import logger as ScoreboardLogger

from data.status import Status
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

        self.update()

    def update(self):
        self.last_update = time.time()

        ScoreboardLogger.log(f"Updating schedule for {datetime.datetime.today()}")

        try:
            self.__fetch_updated_schedule(datetime.datetime.today())
        except Exception as exception:
            ScoreboardLogger.exception("Networking error while refreshing schedule!")
            ScoreboardLogger.exception(exception)

            return Status.FAIL

        self.data.request_next_screen(Screen.GAME)

        return Status.SUCCESS

    def __fetch_updated_schedule(self, date):
        self._games = statsapi.schedule(date.strftime("%Y-%m-%d"))

        self.games = [Game.from_schedule(game) for game in self._games]
