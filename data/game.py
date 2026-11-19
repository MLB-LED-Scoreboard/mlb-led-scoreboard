import time
from datetime import datetime
from typing import Any, Optional


from bullpen.logging import LOGGER
from data import teams
from bullpen.api import UpdateStatus
from data.utils.circular_queue import CircularQueue
from data.uniforms import Uniforms
from data.blurbs import Blurbs
from data.leagues import League, StatAPI
from data.scoreboard import Scoreboard
from data.scoreboard.postgame import Postgame
from data.scoreboard.pregame import Pregame
from bullpen.time_formats import TIME_FORMAT_24H
import data.headers

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config import Config

API_FIELDS = (
    "gameData,game,id,datetime,dateTime,officialDate,flags,noHitter,perfectGame,status,detailedState,abstractGameState,"
    + "reason,probablePitchers,teams,home,away,abbreviation,teamName,record,wins,losses,players,id,boxscoreName,fullName,liveData,plays,"
    + "currentPlay,result,eventType,playEvents,isPitch,pitchData,startSpeed,details,type,code,description,decisions,"
    + "winner,loser,save,id,linescore,outs,balls,strikes,note,inningState,currentInning,currentInningOrdinal,offense,"
    + "batter,inHole,onDeck,first,second,third,defense,pitcher,boxscore,teams,runs,players,seasonStats,pitching,wins,"
    + "losses,saves,era,hits,errors,stats,pitching,numberOfPitches,batting,avg,homeRuns,rbi,battingOrder,"
    + "weather,condition,temp,wind,metaData,timeStamp,"
    + "absChallenges,remaining"
)

SCHEDULE_API_FIELDS = "dates,date,games,status,detailedState,abstractGameState,reason"

GAME_UPDATE_RATE = 10


class Game:
    @staticmethod
    def from_scheduled(game_data: dict[str, Any], config: "Config") -> Optional["Game"]:
        game = Game(
            game_data["league"],
            game_data["game_id"],
            game_data["game_date"],
            game_data.get("national_broadcasts") or [],
            game_data.get("series_status") or "",
            config,
        )
        if game.update(True) == UpdateStatus.SUCCESS:
            return game
        return None

    def __init__(self, league: League, game_id, date, broadcasts, series_status, config: "Config"):
        self.league: League = league
        self.game_id = game_id
        self.date = date
        self.starttime = time.time()
        self._data_wait_queue = CircularQueue(config.sync_amount + 1)
        self._current_data: dict[str, Any] = {}
        self._broadcasts = broadcasts
        self._series_status = series_status
        self._api_refresh_rate = config.api_refresh_rate
        self._status: dict[str, Any] = {}
        self._uniform_data = Uniforms(league.statsapi, game_id, config.uniform_types)
        self._blurb_data = Blurbs(league.statsapi, game_id)

    def update(self, force=False, testing_params={}) -> UpdateStatus:
        if force or self.__should_update():
            self.starttime = time.time()
            try:
                LOGGER.debug("Fetching data for game %s", str(self.game_id))
                live_data = self.league.statsapi.get(
                    "game",
                    {"gamePk": self.game_id, "fields": API_FIELDS} | testing_params,
                    request_kwargs={"headers": data.headers.API_HEADERS},
                )
                # we add a delay to avoid spoilers. During construction, this will still yield live data, but then
                # it will recycle that data until the queue is full.
                self._data_wait_queue.push(live_data)
                self._current_data = self._data_wait_queue.peek()

                # this is odd, but if a game is postponed then the 'game' endpoint gets the
                # rescheduled game, so we need to check the schedule endpoint instead
                if live_data["gameData"]["datetime"]["officialDate"] > self.date:
                    LOGGER.debug("Getting game status from schedule for game with strange date!")
                    try:
                        scheduled = self.league.statsapi.get(
                            "schedule",
                            {"gamePk": self.game_id, "fields": SCHEDULE_API_FIELDS} | self.league.schedule_params,
                            request_kwargs={"headers": data.headers.API_HEADERS},
                        )
                        self._status = next(
                            g["games"][0]["status"] for g in scheduled["dates"] if g["date"] == self.date
                        )
                    except Exception:
                        LOGGER.error("Failed to get game status from schedule")
                else:
                    self._status = self._current_data["gameData"]["status"]

                self._uniform_data.update()
                self._blurb_data.update()
                self.print_game_data_debug()
                return UpdateStatus.SUCCESS
            except Exception:
                LOGGER.exception("Networking Error while refreshing the current game data.")
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

    def __offense_id(self, slot):
        """Player id in an offensive linescore slot -- a base, or batter/onDeck/inHole."""
        try:
            return self._current_data["liveData"]["linescore"]["offense"][slot]["id"]
        except (KeyError, TypeError):
            return None

    def __defense_id(self, slot):
        try:
            return self._current_data["liveData"]["linescore"]["defense"][slot]["id"]
        except (KeyError, TypeError):
            return None

    def __slot_name(self, player_id):
        """Boxscore name for a player id, or "" when there is nobody there."""
        if player_id is None:
            return ""
        try:
            return self.boxscore_name(player_id)
        except (KeyError, TypeError):
            return ""

    def __slot_full_name(self, player_id):
        """As __slot_name, but the player's full name."""
        if player_id is None:
            return ""
        try:
            return self.full_name(player_id)
        except (KeyError, TypeError):
            return ""

    def man_on(self, base):
        return self.__offense_id(base)

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
            except Exception:
                try:
                    stats = self._current_data["liveData"]["boxscore"]["teams"]["away"]["players"][ID]["seasonStats"][
                        "pitching"
                    ]
                except Exception:
                    return ""

        return stats[stat]

    def probable_pitcher_id(self, team):
        try:
            return self._current_data["gameData"]["probablePitchers"][team]["id"]
        except Exception:
            return None

    def decision_pitcher_id(self, decision):
        try:
            return self._current_data["liveData"]["decisions"][decision]["id"]
        except Exception:
            return None

    def batter(self):
        return self.__slot_name(self.__offense_id("batter"))

    def in_hole(self):
        return self.__slot_name(self.__offense_id("inHole"))

    def on_deck(self):
        return self.__slot_name(self.__offense_id("onDeck"))

    def pitcher(self):
        return self.__slot_name(self.__defense_id("pitcher"))

    def batter_stat(self, stat):
        """Season batting stat (avg / homeRuns / rbi) for the current batter."""
        ID = self.__offense_id("batter")
        if ID is None:
            return None
        ID = Game._format_id(ID)
        for side in ("away", "home"):
            try:
                stats = self._current_data["liveData"]["boxscore"]["teams"][side]["players"][ID]["seasonStats"][
                    "batting"
                ]
            except (KeyError, TypeError):
                continue
            return stats.get(stat)
        return None

    def batting_order_for(self, player_id):
        """Spot in the order for a player id, or None.

        battingOrder is a 3-digit string in the boxscore, so "800" is 8th and a
        pinch hitter in that spot is "801" -- hence the integer division.
        """
        if player_id is None:
            return None
        ID = Game._format_id(player_id)
        for side in ("away", "home"):
            try:
                order = self._current_data["liveData"]["boxscore"]["teams"][side]["players"][ID]["battingOrder"]
            except (KeyError, TypeError):
                continue
            try:
                return int(order) // 100
            except (TypeError, ValueError):
                return None
        return None

    def batter_batting_order(self):
        """Spot in the order for the current batter, or None."""
        return self.batting_order_for(self.__offense_id("batter"))

    def on_deck_batting_order(self):
        return self.batting_order_for(self.__offense_id("onDeck"))

    def in_hole_batting_order(self):
        return self.batting_order_for(self.__offense_id("inHole"))

    def pitcher_era(self):
        """Season ERA for the current pitcher, as a string, or None."""
        pitcher_id = self.__defense_id("pitcher")
        if pitcher_id is None:
            return None
        try:
            era = self.pitcher_stat(pitcher_id, "era")
        except KeyError:
            return None
        return str(era) if era != "" else None

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
        except Exception:
            return None

    def current_pitcher_pitch_count(self):
        try:
            pitcher_id = self._current_data["liveData"]["linescore"]["defense"]["pitcher"]["id"]
            ID = Game._format_id(pitcher_id)
            try:
                return self._current_data["liveData"]["boxscore"]["teams"]["away"]["players"][ID]["stats"]["pitching"][
                    "numberOfPitches"
                ]
            except Exception:
                return self._current_data["liveData"]["boxscore"]["teams"]["home"]["players"][ID]["stats"]["pitching"][
                    "numberOfPitches"
                ]
        except Exception:
            return 0

    def note(self):
        try:
            return self._current_data["liveData"]["linescore"]["note"]
        except Exception:
            return None

    def reason(self):
        try:
            return self._status["reason"]
        except Exception:
            try:
                return self._status["detailedState"].split(":")[1].strip()
            except Exception:
                return None

    def broadcasts(self):
        return self._broadcasts

    def series_status(self):
        return self._series_status

    def abs_challenges_remaining(self, side):
        try:
            return self._current_data["gameData"]["absChallenges"][side]["remaining"]
        except (KeyError, TypeError):
            return None

    def current_play_result(self):
        result = self._current_data["liveData"]["plays"].get("currentPlay", {}).get("result", {}).get("eventType", "")
        if result == "strikeout" and (
            "called"
            in self._current_data["liveData"]["plays"].get("currentPlay", {}).get("result", {}).get("description", "")
        ):
            result += "_looking"
        return result

    def last_pitch_sentence(self):
        """The pitch just thrown, in long form.

        "Andrew Sears throws a 94mph Four-Seam Fastball, called strike"

        Built from the last playEvent: `pitchData.startSpeed`,
        `details.type.description` for the pitch, and `details.description` for the
        call. All three already come through API_FIELDS.
        """
        try:
            events = self._current_data["liveData"]["plays"].get("currentPlay", {}).get("playEvents", [])
            event = events[-1]
        except (KeyError, TypeError, IndexError):
            return ""
        if not event.get("isPitch", False):
            return ""

        details = event.get("details", {})
        pitch = (details.get("type") or {}).get("description", "")
        speed = (event.get("pitchData") or {}).get("startSpeed")
        if not pitch and speed is None:
            return ""

        pitcher_id = self.__defense_id("pitcher")
        sentence = self.__slot_full_name(pitcher_id) or self.__slot_name(pitcher_id) or "Pitcher"
        if speed is not None and pitch:
            sentence += f" throws {_article(round(speed))} {round(speed)}mph {pitch}"
        elif pitch:
            sentence += f" throws {_article(pitch)} {pitch}"
        else:
            sentence += f" throws {round(speed)}mph"

        call = details.get("description", "")
        # Skip a call that just repeats the pitch type, and skip "In play, ..." --
        # the resolved play arrives seconds later and says what actually happened,
        # so announcing "in play, out(s)" first is both clumsy and redundant.
        if call and call.lower() != pitch.lower() and not call.lower().startswith("in play"):
            sentence += f" ({call})"
        return sentence

    def current_play_description(self):
        """The most informative text available for what is happening right now.

        The resolved play when there is one -- MLB only populates it once an at-bat
        ends -- otherwise the pitch just thrown, which refreshes every delivery and
        so covers the rest of an at-bat. Empty when there is nothing live to say,
        such as across a pitching change.
        """
        try:
            resolved = (
                self._current_data["liveData"]["plays"].get("currentPlay", {}).get("result", {}).get("description", "")
            )
        except (KeyError, TypeError):
            resolved = ""

        return resolved or self.last_pitch_sentence()

    def game_recap_blurb(self):
        return self._blurb_data.recap()

    def game_preview_blurb(self):
        return self._blurb_data.preview()

    def __should_update(self):
        if self._status.get("abstractGameState") == "Final":
            return False
        endtime = time.time()
        time_delta = endtime - self.starttime
        return time_delta >= self._api_refresh_rate

    @staticmethod
    def _format_id(player):
        return player if "ID" in str(player) else "ID" + str(player)

    def __eq__(self, value):
        if isinstance(value, Game):
            return self.game_id == value.game_id
        return False

    def print_game_data_debug(self):
        LOGGER.debug("Game Data Refreshed: %s", self._current_data["gameData"]["game"]["id"])
        LOGGER.debug("Game is %d seconds behind", self.current_delay())
        LOGGER.debug("Pre: %s", Pregame(self, TIME_FORMAT_24H))
        LOGGER.debug("Live: %s", Scoreboard(self))
        LOGGER.debug("Final: %s", Postgame(self))


def _article(value) -> str:
    """ "a" or "an" for a speed or a pitch name.

    Spoken aloud, "88" starts with a vowel ("eighty-eight"), so "a 88mph Slider"
    reads wrong on a line that is otherwise prose.
    """
    text = str(value)
    if text[:1] == "8":
        return "an"
    return "an" if text[:1].lower() in "aeiou" else "a"
