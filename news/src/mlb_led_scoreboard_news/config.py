import bullpen.api as api
from bullpen.time_formats import os_datetime_format
from bullpen.logging import LOGGER

DEFAULT_PREFERRED_TEAMS = ["Cubs"]


class Config(api.Config):
    def __init__(self, config: api.MLBConfig) -> None:
        self.date = config.parse_today()
        self.year = self.date.year
        self.time_format = config.time_format
        self.scrolling_speed = config.scrolling_speed

        json_weather = config.for_plugin("weather")
        self.weather_apikey = json_weather["apikey"]
        self.weather_location = json_weather["location"]
        self.weather_metric_units = json_weather["metric_units"]

        json_news = config.for_plugin("news_ticker")
        self.preferred_teams = json_news["teams"]
        self.news_ticker_traderumors = json_news["traderumors"]
        self.news_ticker_mlb_news = json_news["mlb_news"]
        self.news_ticker_countdowns = json_news["countdowns"]
        self.news_ticker_date = json_news["date"]
        self.news_ticker_date_format = os_datetime_format(json_news["date_format"])
        self.check_preferred_teams()

    def check_preferred_teams(self):
        if not isinstance(self.preferred_teams, str) and not isinstance(self.preferred_teams, list):
            LOGGER.warning(
                "preferred_teams should be an array of team names or a single team name string."
                "Using default preferred_teams, {}".format(DEFAULT_PREFERRED_TEAMS)
            )
            self.preferred_teams = DEFAULT_PREFERRED_TEAMS
        if isinstance(self.preferred_teams, str):
            team = self.preferred_teams
            self.preferred_teams = [team]
