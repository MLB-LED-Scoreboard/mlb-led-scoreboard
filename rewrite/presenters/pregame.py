import tzlocal


class PregamePresenter:
    TBD = "TBD"

    def __init__(self, game, config):
        self.game = game
        self.config = config

        self.home_team = game.home_abbreviation()
        self.away_team = game.away_abbreviation()

        # TODO: No weather object yet.
        # self.pregame_weather = game.pregame_weather()

        self.status = game.status

        away_id = game.probable_pitcher_id("away")
        if away_id is not None:
            name = game.full_name(away_id)
            wins = game.pitcher_stat(away_id, "wins", "away")
            losses = game.pitcher_stat(away_id, "losses", "away")
            era = game.pitcher_stat(away_id, "era", "away")
            self.away_starter = "{} ({}-{} {} ERA)".format(name, wins, losses, era)
        else:
            self.away_starter = PregamePresenter.TBD

        home_id = game.probable_pitcher_id("home")
        if home_id is not None:
            name = game.full_name(home_id)
            wins = game.pitcher_stat(home_id, "wins", "home")
            losses = game.pitcher_stat(home_id, "losses", "home")
            era = game.pitcher_stat(home_id, "era", "home")
            self.home_starter = "{} ({}-{} {} ERA)".format(name, wins, losses, era)
        else:
            self.home_starter = PregamePresenter.TBD

        # TODO: No broadcasts yet
        # self.national_broadcasts = game.broadcasts()
        # self.series_status = game.series_status()

    @property
    def start_time(self):
        """Converts MLB's pregame times (UTC) into the local time zone"""
        try:
            time_str = "{}:%M".format(self.config.time_format)
            if self.config.time_format == self.config.TIME_FORMAT_12H:
                time_str += "%p"

            return self.game.datetime().astimezone(tzlocal.get_localzone()).strftime(time_str)
        except:
            return PregamePresenter.TBD

    def pregame_info(self):
        parts = [self.__pitcher_matchup(), self.__broadcasts(), self.__weather(), self.__playoff_series_status()]

        return " ".join(filter(None, parts))

    def __pitcher_matchup(self):
        return self.away_starter + " vs " + self.home_starter

    def __broadcasts(self):
        broadcasts = self.game.broadcasts()

        if len(broadcasts) > 0:
            return "TV: " + ", ".join(broadcasts)

        return None

    def __weather(self):
        if not self.config.pregame_weather:
            return None

        weather = self.game.pregame_weather()

        try:
            return f"{weather['condition']} and {weather['temp']}\N{DEGREE SIGN} wind {weather['wind']}"
        except KeyError:
            return None

    def __playoff_series_status(self):
        # TODO: Re-add series status
        return None

        # if self.game.is_playoff:
        #   return self.game.series_status

    def __str__(self):
        s = "<{} {}> {} @ {}; {}; {} vs {}; Forecast: {}; TV: {}".format(
            self.__class__.__name__,
            hex(id(self)),
            self.away_team,
            self.home_team,
            self.start_time,
            self.away_starter,
            self.home_starter,
            self.pregame_info(),
        )
        return s
