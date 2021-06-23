import time
from datetime import datetime

import statsapi

import debug
from data.update import UpdateStatus

API_FIELDS = (
    "gameData,game,id,datetime,dateTime,flags,noHitter,perfectGame,status,detailedState,abstractGameState,"
    + "probablePitchers,teams,home,away,abbreviation,teamName,players,id,boxscoreName,fullName,liveData,plays,"
    + "currentPlay,result,eventType,decisions,winner,loser,save,id,linescore,outs,balls,strikes,note,inningState,"
    + "currentInning,currentInningOrdinal,offense,batter,inHole,onDeck,first,second,third,defense,pitcher,boxscore,"
    + "teams,runs,players,seasonStats,pitching,wins,losses,saves,era"
)

GAME_UPDATE_RATE = 10


class Game:
    @classmethod
    def from_ID(cls, game_id):
        game = Game(game_id)
        if game.update(True) == UpdateStatus.SUCCESS:
            return game
        return None

    def __init__(self, game_id):
        self.game_id = game_id
        self.starttime = time.time()
        self._data = {}

    def update(self, force=False) -> UpdateStatus:
        if force or self.__should_update():
            self.starttime = time.time()
            try:
                debug.log("Fetching data for game %s", str(self.game_id))
                self._data = statsapi.get("game", {"gamePk": self.game_id, "fields": API_FIELDS})
                return UpdateStatus.SUCCESS
            except:
                debug.error("Networking Error while refreshing the current game data.")
                return UpdateStatus.FAIL
        return UpdateStatus.DEFERRED

    def datetime(self):
        time = self._data["gameData"]["datetime"]["dateTime"]
        return datetime.fromisoformat(time.replace("Z", "+00:00"))

    def home_name(self):
        return self._data["gameData"]["teams"]["home"]["teamName"]

    def home_abbreviation(self):
        return self._data["gameData"]["teams"]["home"]["abbreviation"]

    def away_name(self):
        return self._data["gameData"]["teams"]["away"]["teamName"]

    def away_abbreviation(self):
        return self._data["gameData"]["teams"]["away"]["abbreviation"]

    def status(self):
        return self._data["gameData"]["status"]["detailedState"]

    def home_score(self):
        return self._data["liveData"]["linescore"]["teams"]["home"].get("runs", 0)

    def away_score(self):
        return self._data["liveData"]["linescore"]["teams"]["away"].get("runs", 0)

    def winning_team(self):
        if self._data["gameData"]["status"]["abstractGameState"] == "Final":
            if self.home_score() > self.away_score():
                return "home"
            if self.home_score() < self.away_score():
                return "away"
        return None

    def losing_team(self):
        winner = self.winning_team()
        if winner is not None:
            if winner == "home":
                return "away"
            return "home"
        return None

    def inning_state(self):
        return self._data["liveData"]["linescore"].get("inningState", "Top")

    def inning_number(self):
        return self._data["liveData"]["linescore"].get("currentInning", 0)

    def inning_ordinal(self):
        return self._data["liveData"]["linescore"].get("currentInningOrdinal", 0)

    def features_team(self, team):
        return team in [
            self._data["gameData"]["teams"]["away"]["teamName"],
            self._data["gameData"]["teams"]["home"]["teamName"],
        ]

    def is_no_hitter(self):
        return self._data["gameData"]["flags"]["noHitter"]

    def is_perfect_game(self):
        return self._data["gameData"]["flags"]["perfectGame"]

    def man_on(self, base):
        try:
            id = self._data["liveData"]["linescore"]["offense"][base]["id"]
        except KeyError:
            return None
        else:
            return id

    def full_name(self, player):
        ID = Game._format_id(player)
        return self._data["gameData"]["players"][ID]["fullName"]

    def boxscore_name(self, player):
        ID = Game._format_id(player)
        return self._data["gameData"]["players"][ID]["boxscoreName"]

    def pitcher_stat(self, player, stat, team=None):
        ID = Game._format_id(player)

        if team is not None:
            stats = self._data["liveData"]["boxscore"]["teams"][team]["players"][ID]["seasonStats"]["pitching"]
        else:
            try:
                stats = self._data["liveData"]["boxscore"]["teams"]["home"]["players"][ID]["seasonStats"]["pitching"]
            except:
                try:
                    stats = self._data["liveData"]["boxscore"]["teams"]["away"]["players"][ID]["seasonStats"][
                        "pitching"
                    ]
                except:
                    return ""

        return stats[stat]

    def probable_pitcher_id(self, team):
        try:
            return self._data["gameData"]["probablePitchers"][team]["id"]
        except:
            return None

    def decision_pitcher_id(self, decision):
        try:
            return self._data["liveData"]["decisions"][decision]["id"]
        except:
            return None

    def batter(self):
        try:
            batter_id = self._data["liveData"]["linescore"]["offense"]["batter"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def in_hole(self):
        try:
            batter_id = self._data["liveData"]["linescore"]["offense"]["inHole"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def on_deck(self):
        try:
            batter_id = self._data["liveData"]["linescore"]["offense"]["onDeck"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def pitcher(self):
        try:
            batter_id = self._data["liveData"]["linescore"]["defense"]["pitcher"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def balls(self):
        return self._data["liveData"]["linescore"].get("balls", 0)

    def strikes(self):
        return self._data["liveData"]["linescore"].get("strikes", 0)

    def outs(self):
        return self._data["liveData"]["linescore"].get("outs", 0)

    def note(self):
        try:
            return self._data["liveData"]["linescore"]["note"]
        except:
            return None

    def reason(self):
        try:
            return self._data["gameData"]["status"]["reason"]
        except:
            try:
                return self._data["gameData"]["status"]["detailedState"].split(":")[1]
            except:
                return None

    def current_play_result(self):
        return self._data["liveData"]["plays"].get("currentPlay", {}).get("result", {}).get("eventType", None)

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= GAME_UPDATE_RATE

    @classmethod
    def _format_id(cls, player):
        return player if "ID" in str(player) else "ID" + str(player)
