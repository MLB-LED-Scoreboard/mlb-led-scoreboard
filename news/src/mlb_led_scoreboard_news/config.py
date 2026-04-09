import bullpen.api as api
from bullpen.time_formats import os_datetime_format
from bullpen.logging import LOGGER

DEFAULT_PREFERRED_TEAMS = ["Cubs"]


class Config(api.PluginConfig):
    def __init__(self, config: api.MLBConfig) -> None:
        self.date = config.parse_today()
        self.time_format = config.time_format
        self.scrolling_speed = config.scrolling_speed

        # note: we can safely do raw accesses here because we are built-in
        # and have the .example.json files as a crutch
        # 3rd party plugins should use .get!
        self.weather_apikey = config.plugin_config["apikey"]
        self.weather_location = config.plugin_config["location"]
        self.weather_metric_units = config.plugin_config["metric_units"]

        self.preferred_teams = config.plugin_config["teams"]
        self.news_ticker_traderumors = config.plugin_config["traderumors"]
        self.news_ticker_mlb_news = config.plugin_config["mlb_news"]
        self.news_ticker_countdowns = config.plugin_config["countdowns"]
        self.news_ticker_date = config.plugin_config["date"]
        self.news_ticker_date_format = os_datetime_format(config.plugin_config["date_format"])
        self.custom_countdowns = config.plugin_config.get("events", [])
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
