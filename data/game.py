import time
from datetime import datetime
from typing import Optional

import statsapi

import debug
from data import teams
from data.update import UpdateStatus
from data.delay_buffer import CircularQueue
from data.uniforms import Uniforms
import data.headers

API_FIELDS = (
    "gameData,game,id,datetime,dateTime,officialDate,flags,noHitter,perfectGame,status,detailedState,abstractGameState,"
    + "reason,probablePitchers,teams,home,away,abbreviation,teamName,record,wins,losses,players,id,boxscoreName,fullName,liveData,plays,"
    + "currentPlay,result,eventType,playEvents,isPitch,pitchData,startSpeed,details,type,code,description,decisions,"
    + "winner,loser,save,id,linescore,outs,balls,strikes,note,inningState,currentInning,currentInningOrdinal,offense,"
    + "batter,inHole,onDeck,first,second,third,defense,pitcher,boxscore,teams,runs,players,seasonStats,pitching,wins,"
    + "losses,saves,era,hits,errors,stats,pitching,numberOfPitches,weather,condition,temp,wind,metaData,timeStamp"
)

SCHEDULE_API_FIELDS = "dates,date,games,status,detailedState,abstractGameState,reason"


class Game:
    @staticmethod
    def from_scheduled(game_data, delay, api_refresh_rate) -> Optional["Game"]:
        game = Game(
            game_data["game_id"],
            game_data["game_date"],
            game_data.get("national_broadcasts") or [],
            game_data.get("series_status") or "",
            delay,
            api_refresh_rate,
        )
        if game.update(True) == UpdateStatus.SUCCESS:
            return game
        return None

    def __init__(self, game_id, date, broadcasts, series_status, sync_rate, api_refresh_rate):
        self.game_id = game_id
        self.date = date
        self.starttime = time.time()
        self._data_wait_queue = CircularQueue(sync_rate + 1)
        self._current_data = {}
        self._broadcasts = broadcasts
        self._series_status = series_status
        self._api_refresh_rate = api_refresh_rate
        self._status = {}
        self._uniform_data = Uniforms(game_id)

    def update(self, force=False, testing_params={}) -> UpdateStatus:
        if force or self.__should_update():
            self.starttime = time.time()
            try:
                debug.log("Fetching data for game %s", str(self.game_id))
                live_data = statsapi.get("game", {"gamePk": self.game_id, "fields": API_FIELDS} | testing_params, request_kwargs={"headers": data.headers.API_HEADERS} )
                # we add a delay to avoid spoilers. During construction, this will still yield live data, but then
                # it will recycle that data until the queue is full.
                self._data_wait_queue.push(live_data)
                self._current_data = self._data_wait_queue.peek()
                self._status = self._current_data["gameData"]["status"]
                if live_data["gameData"]["datetime"]["officialDate"] > self.date:
                    # this is odd, but if a game is postponed then the 'game' endpoint gets the rescheduled game
                    debug.log("Getting game status from schedule for game with strange date!")
                    try:
                        scheduled = statsapi.get(
                            "schedule", {"gamePk": self.game_id, "sportId": 1, "fields": SCHEDULE_API_FIELDS}, request_kwargs={"headers": data.headers.API_HEADERS}
                        )
                        self._status = next(
                            g["games"][0]["status"] for g in scheduled["dates"] if g["date"] == self.date
                        )
                    except:
                        debug.error("Failed to get game status from schedule")

                self._uniform_data.update()
                return UpdateStatus.SUCCESS
            except:
                debug.exception("Networking Error while refreshing the current game data.")
                return UpdateStatus.FAIL
        return UpdateStatus.DEFERRED

    def datetime(self):
        time = self._current_data["gameData"]["datetime"]["dateTime"]
        return datetime.fromisoformat(time.replace("Z", "+00:00"))

    def current_delay(self):
        return (len(self._data_wait_queue) - 1) * self._api_refresh_rate

    def home_name(self):
        return teams.TEAM_ID_NAME.get(
            self._current_data["gameData"]["teams"]["home"]["id"],
            self._current_data["gameData"]["teams"]["home"]["teamName"],
        )

    def home_abbreviation(self):
        return teams.TEAM_ID_ABBR.get(
            self._current_data["gameData"]["teams"]["home"]["id"],
            self._current_data["gameData"]["teams"]["home"]["abbreviation"],
        )

    def home_record(self):
        return self._current_data["gameData"]["teams"]["home"]["record"] or {}

    def home_special_uniforms(self):
        return self._uniform_data.home_special_uniform()

    def away_special_uniforms(self):
        return self._uniform_data.away_special_uniform()

    def away_record(self):
        return self._current_data["gameData"]["teams"]["away"]["record"] or {}

    def pregame_weather(self):
        try:
            wx = (
                self._current_data["gameData"]["weather"]["condition"]
                + " and "
                + self._current_data["gameData"]["weather"]["temp"]
                + "\N{DEGREE SIGN}"
                + " wind "
                + self._current_data["gameData"]["weather"]["wind"]
            )
        except KeyError:
            return None
        else:
            return wx

    def away_name(self):
        return teams.TEAM_ID_NAME.get(
            self._current_data["gameData"]["teams"]["away"]["id"],
            self._current_data["gameData"]["teams"]["away"]["teamName"],
        )

    def away_abbreviation(self):
        return teams.TEAM_ID_ABBR.get(
            self._current_data["gameData"]["teams"]["away"]["id"],
            self._current_data["gameData"]["teams"]["away"]["abbreviation"],
        )

    def status(self):
        return self._status["detailedState"]

    def home_score(self):
        return self._current_data["liveData"]["linescore"]["teams"]["home"].get("runs", 0)

    def away_score(self):
        return self._current_data["liveData"]["linescore"]["teams"]["away"].get("runs", 0)

    def home_hits(self):
        return self._current_data["liveData"]["linescore"]["teams"]["home"].get("hits", 0)

    def away_hits(self):
        return self._current_data["liveData"]["linescore"]["teams"]["away"].get("hits", 0)

    def home_errors(self):
        return self._current_data["liveData"]["linescore"]["teams"]["home"].get("errors", 0)

    def away_errors(self):
        return self._current_data["liveData"]["linescore"]["teams"]["away"].get("errors", 0)

    def winning_team(self):
        if self._status["abstractGameState"] == "Final":
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
        return self._current_data["liveData"]["linescore"].get("inningState", "Top")

    def inning_number(self):
        return self._current_data["liveData"]["linescore"].get("currentInning", 0)

    def inning_ordinal(self):
        return self._current_data["liveData"]["linescore"].get("currentInningOrdinal", 0)

    def features_team(self, team):
        return team in [
            self._current_data["gameData"]["teams"]["away"]["teamName"],
            self._current_data["gameData"]["teams"]["home"]["teamName"],
        ]

    def is_no_hitter(self):
        return self._current_data["gameData"]["flags"]["noHitter"]

    def is_perfect_game(self):
        return self._current_data["gameData"]["flags"]["perfectGame"]

    def man_on(self, base):
        try:
            id = self._current_data["liveData"]["linescore"]["offense"][base]["id"]
        except KeyError:
            return None
        else:
            return id

    def full_name(self, player):
        ID = Game._format_id(player)
        return self._current_data["gameData"]["players"][ID]["fullName"]

    def boxscore_name(self, player):
        ID = Game._format_id(player)
        return self._current_data["gameData"]["players"][ID]["boxscoreName"]

    def pitcher_stat(self, player, stat, team=None):
        ID = Game._format_id(player)

        if team is not None:
            stats = self._current_data["liveData"]["boxscore"]["teams"][team]["players"][ID]["seasonStats"]["pitching"]
        else:
            try:
                stats = self._current_data["liveData"]["boxscore"]["teams"]["home"]["players"][ID]["seasonStats"][
                    "pitching"
                ]
            except:
                try:
                    stats = self._current_data["liveData"]["boxscore"]["teams"]["away"]["players"][ID]["seasonStats"][
                        "pitching"
                    ]
                except:
                    return ""

        return stats[stat]

    def probable_pitcher_id(self, team):
        try:
            return self._current_data["gameData"]["probablePitchers"][team]["id"]
        except:
            return None

    def decision_pitcher_id(self, decision):
        try:
            return self._current_data["liveData"]["decisions"][decision]["id"]
        except:
            return None

    def batter(self):
        try:
            batter_id = self._current_data["liveData"]["linescore"]["offense"]["batter"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def in_hole(self):
        try:
            batter_id = self._current_data["liveData"]["linescore"]["offense"]["inHole"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def on_deck(self):
        try:
            batter_id = self._current_data["liveData"]["linescore"]["offense"]["onDeck"]["id"]
            return self.boxscore_name(batter_id)
        except:
            return ""

    def pitcher(self):
        try:
            pitcher_id = self._current_data["liveData"]["linescore"]["defense"]["pitcher"]["id"]
            return self.boxscore_name(pitcher_id)
        except:
            return ""

    def balls(self):
        return self._current_data["liveData"]["linescore"].get("balls", 0)

    def strikes(self):
        return self._current_data["liveData"]["linescore"].get("strikes", 0)

    def outs(self):
        return self._current_data["liveData"]["linescore"].get("outs", 0)

    def last_pitch(self):
        try:
            play = self._current_data["liveData"]["plays"].get("currentPlay", {}).get("playEvents", [{}])[-1]
            if play.get("isPitch", False):
                return (
                    play["pitchData"].get("startSpeed", 0),
                    play["details"]["type"]["code"],
                    play["details"]["type"]["description"],
                )
        except:
            return None

    def current_pitcher_pitch_count(self):
        try:
            pitcher_id = self._current_data["liveData"]["linescore"]["defense"]["pitcher"]["id"]
            ID = Game._format_id(pitcher_id)
            try:
                return self._current_data["liveData"]["boxscore"]["teams"]["away"]["players"][ID]["stats"]["pitching"][
                    "numberOfPitches"
                ]
            except:
                return self._current_data["liveData"]["boxscore"]["teams"]["home"]["players"][ID]["stats"]["pitching"][
                    "numberOfPitches"
                ]
        except:
            return 0

    def note(self):
        try:
            return self._current_data["liveData"]["linescore"]["note"]
        except:
            return None

    def reason(self):
        try:
            return self._status["reason"]
        except:
            try:
                return self._status["detailedState"].split(":")[1].strip()
            except:
                return None

    def broadcasts(self):
        return self._broadcasts

    def series_status(self):
        return self._series_status

    def current_play_result(self):
        result = self._current_data["liveData"]["plays"].get("currentPlay", {}).get("result", {}).get("eventType", "")
        if result == "strikeout" and (
            "called"
            in self._current_data["liveData"]["plays"].get("currentPlay", {}).get("result", {}).get("description", "")
        ):
            result += "_looking"
        return result

    def __should_update(self):
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= self._api_refresh_rate

    @staticmethod
    def _format_id(player):
        return player if "ID" in str(player) else "ID" + str(player)
