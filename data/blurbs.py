import time

from bullpen.logging import LOGGER
import data.headers
from data.leagues import StatAPI

UPDATE_RATE = 60 * 5


# separate API call from the game_content endpoint, so we don't fold this into
# the Game data updates
class Blurbs:
    def __init__(self, statsapi: StatAPI, game_id: str) -> None:
        self.statsapi: StatAPI = statsapi
        self.game_id = game_id
        self._content: dict = {}
        self.starttime = time.time()
        self.update(force=True)

    def recap(self):
        return self._blurb("recap")

    def preview(self):
        return self._blurb("preview")

    def update(self, force=False):
        if not force and not self.__should_update():
            return

        try:
            self._content = self.statsapi.get(
                "game_content",
                {"gamePk": self.game_id},
                request_kwargs={"headers": data.headers.API_HEADERS},
            )
            self.starttime = time.time()
        except Exception:
            LOGGER.exception(f"Error while fetching game {self.game_id} blurb content")

    def _blurb(self, section):
        try:
            mlb = self._content["editorial"][section]["mlb"]
            headline = mlb.get("headline", "")
            subhead = mlb.get("subhead", "")
            return " ".join((" - ".join(filter(None, [headline, subhead]))).split())
        except (KeyError, TypeError):
            return ""

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= UPDATE_RATE
