from datetime import datetime

import mlbgame
import pytz
import tzlocal

import debug


class Pregame:
    def __init__(self, game_data, time_format):
        self.home_team = game_data["gameData"]["teams"]["home"]["abbreviation"]
        self.away_team = game_data["gameData"]["teams"]["away"]["abbreviation"]
        self.time_format = time_format

        try:
            self.start_time = self.__convert_time(
                game_data["gameData"]["datetime"]["time"] + game_data["gameData"]["datetime"]["ampm"]
            )
        except:
            self.start_time = "TBD"

        self.status = game_data["gameData"]["status"]["detailedState"]

        try:
            away_id = "ID" + str(game_data["gameData"]["probablePitchers"]["away"]["id"])
            away_name = game_data["gameData"]["players"][away_id]["boxscore_name"]
            away_stats = game_data["liveData"]["boxscore"]["teams"]["away"]["players"][away_id]["seasonStats"][
                "pitching"
            ]
            self.away_starter = "({}-{} {} ERA)".format(
                away_name, away_stats["wins"], away_stats["losses"], away_stats["era"]
            )
        except:
            self.away_starter = "TBD"

        try:
            home_id = "ID" + str(game_data["gameData"]["probablePitchers"]["home"]["id"])
            home_name = game_data["gameData"]["players"][home_id]["boxscore_name"]
            home_stats = game_data["liveData"]["boxscore"]["teams"]["home"]["players"][home_id]["seasonStats"][
                "pitching"
            ]
            self.home_starter = "({}-{} {} ERA)".format(
                home_name, home_stats["wins"], home_stats["losses"], home_stats["era"]
            )
        except:
            self.home_starter = "TBD"

    def __convert_time(self, time):
        """Converts MLB's pregame times (Eastern) into the local time zone"""
        time_str = "{}:%M".format(self.time_format)
        if self.time_format == "%I":
            time_str += "%p"

        game_time_eastern = datetime.strptime(time, "%I:%M%p")
        now = datetime.now()
        game_time_eastern = game_time_eastern.replace(year=now.year, month=now.month, day=now.day)
        eastern_tz = pytz.timezone("America/New_York")
        game_time_eastern = eastern_tz.localize(game_time_eastern)
        return game_time_eastern.astimezone(tzlocal.get_localzone()).strftime(time_str)

    def __str__(self):
        s = "<{} {}> {} @ {}; {}; {} vs {}".format(
            self.__class__.__name__,
            hex(id(self)),
            self.away_team,
            self.home_team,
            self.start_time,
            self.away_starter,
            self.home_starter,
        )
        return s
