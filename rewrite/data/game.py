import statsapi, time

from datetime import datetime as dt

from data.update_status import UpdateStatus
from data import status as GameState

from utils import logger as ScoreboardLogger


class Game:
    API_FIELDS = (
        "gameData,game,id,datetime,dateTime,officialDate,flags,noHitter,perfectGame,status,detailedState,abstractGameState,"
        + "reason,probablePitchers,teams,home,away,abbreviation,teamName,record,wins,losses,players,id,boxscoreName,fullName,liveData,plays,"
        + "currentPlay,result,eventType,playEvents,isPitch,pitchData,startSpeed,details,type,code,description,decisions,"
        + "winner,loser,save,id,linescore,outs,balls,strikes,note,inningState,currentInning,currentInningOrdinal,offense,"
        + "batter,inHole,onDeck,first,second,third,defense,pitcher,boxscore,teams,runs,players,seasonStats,pitching,wins,"
        + "losses,saves,era,hits,errors,stats,pitching,numberOfPitches,weather,condition,temp,wind"
    )

    SCHEDULE_API_FIELDS = "dates,date,games,status,detailedState,abstractGameState,reason"

    REFRESH_RATE = 10  # seconds

    @staticmethod
    def from_schedule(game_data, update=False):
        game = Game(game_data)

        if not update or game.update(True) == UpdateStatus.SUCCESS:
            return game

        return None

    def __init__(self, data):
        self.data = data

        self.id = data["game_id"]
        self.date = data["game_date"]
        self.status = data["status"]
        self.updated_at = time.time()

        self._status = None

    def update(self, force=False):
        if force or self.__should_update():
            self.updated_at = time.time()
            try:
                ScoreboardLogger.log("Fetching data for game %s", str(self.id))
                live_data = statsapi.get("game", {"gamePk": self.id, "fields": Game.API_FIELDS})
                # TODO: Re-implement the delay buffer
                # we add a delay to avoid spoilers. During construction, this will still yield live data, but then
                # it will recycle that data until the queue is full.
                # self._data_wait_queue.push(live_data)
                # self._api_data = self._data_wait_queue.peek()
                self.data = live_data
                self._status = self.data["gameData"]["status"]

                ScoreboardLogger.log(self._status)

                if live_data["gameData"]["datetime"]["officialDate"] > self.date:
                    # this is odd, but if a game is postponed then the 'game' endpoint gets the rescheduled game
                    ScoreboardLogger.log("Getting game status from schedule for game with strange date!")
                    try:
                        scheduled = statsapi.get(
                            "schedule", {"gamePk": self.id, "sportId": 1, "fields": Game.SCHEDULE_API_FIELDS}
                        )
                        self._status = next(
                            game["games"][0]["status"] for game in scheduled["dates"] if game["date"] == self.date
                        )

                    except Exception as exception:
                        ScoreboardLogger.error(exception)
                        ScoreboardLogger.error("Failed to get game status from schedule")

                if self._status is None:
                    self.status = GameState.UNKNOWN
                else:
                    self.status = self._status.get("detailedState", GameState.UNKNOWN)

                return UpdateStatus.SUCCESS
            except Exception as exception:
                ScoreboardLogger.exception(exception)
                ScoreboardLogger.exception("Networking Error while refreshing the current game data.")

                return UpdateStatus.FAIL

        return UpdateStatus.DEFERRED

    def is_pregame(self):
        """Returns whether the game is in a pregame state"""
        return self.status in GameState.GAME_STATE_PREGAME

    def is_complete(self):
        """Returns whether the game has been completed"""
        return self.status in GameState.GAME_STATE_COMPLETE

    def is_live(self):
        """Returns whether the game is currently live"""
        return self.status in GameState.GAME_STATE_LIVE

    def is_irregular(self):
        """Returns whether game is in an irregular state, such as delayed, postponed, cancelled,
        or in a challenge."""
        return self.status in GameState.GAME_STATE_IRREGULAR

    def is_fresh(self):
        """Returns whether the game is in progress or is very recently complete. Game Over
        comes between In Progress and Final and allows a few minutes to see the final outcome before
        the rotation kicks in."""
        return self.status in GameState.GAME_STATE_FRESH

    def is_inning_break(inning_state):
        """Returns whether a game is in an inning break (mid/end). Pass in the inning state."""
        return inning_state not in GameState.GAME_STATE_INNING_LIVE

    def datetime(self):
        time_utc = self.data["gameData"]["datetime"]["dateTime"]

        return dt.fromisoformat(time_utc.replace("Z", "+00:00"))

    def home_score(self):
        return self.data["liveData"]["linescore"]["teams"]["home"].get("runs", 0)

    def away_score(self):
        return self.data["liveData"]["linescore"]["teams"]["away"].get("runs", 0)

    def home_hits(self):
        return self.data["liveData"]["linescore"]["teams"]["home"].get("hits", 0)

    def away_hits(self):
        return self.data["liveData"]["linescore"]["teams"]["away"].get("hits", 0)

    def home_errors(self):
        return self.data["liveData"]["linescore"]["teams"]["home"].get("errors", 0)

    def away_errors(self):
        return self.data["liveData"]["linescore"]["teams"]["away"].get("errors", 0)

    def winning_team(self):
        if self.status == GameState.FINAL:
            if self.home_score() > self.away_score():
                return "home"
            if self.home_score() < self.away_score():
                return "away"

        return None

    def losing_team(self):
        opposite = {"home": "away", "away": "home"}

        return opposite.get(self.winning_team(), None)

    def series_status(self):
        # TODO: Reimplement series status
        return "0-0"
