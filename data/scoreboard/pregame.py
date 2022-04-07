import tzlocal

from data.game import Game

PITCHER_TBD = "TBD"


class Pregame:
    def __init__(self, game: Game, time_format):
        self.home_team = game.home_abbreviation()
        self.away_team = game.away_abbreviation()
        self.time_format = time_format

        try:
            self.start_time = self.__convert_time(game.datetime())
        except:
            self.start_time = "TBD"

        self.status = game.status()

        away_id = game.probable_pitcher_id("away")
        if away_id is not None:
            name = game.full_name(away_id)
            wins = game.pitcher_stat(away_id, "wins", "away")
            losses = game.pitcher_stat(away_id, "losses", "away")
            era = game.pitcher_stat(away_id, "era", "away")
            self.away_starter = "{} ({}-{} {} ERA)".format(name, wins, losses, era)
        else:
            self.away_starter = PITCHER_TBD

        home_id = game.probable_pitcher_id("home")
        if home_id is not None:
            name = game.full_name(home_id)
            wins = game.pitcher_stat(home_id, "wins", "home")
            losses = game.pitcher_stat(home_id, "losses", "home")
            era = game.pitcher_stat(home_id, "era", "home")
            self.home_starter = "{} ({}-{} {} ERA)".format(name, wins, losses, era)
        else:
            self.home_starter = PITCHER_TBD

    def __convert_time(self, game_time_utc):
        """Converts MLB's pregame times (UTC) into the local time zone"""
        time_str = "{}:%M".format(self.time_format)
        if self.time_format == "%I":
            time_str += "%p"
        return game_time_utc.astimezone(tzlocal.get_localzone()).strftime(time_str)

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
