import json
import os
import sys

from datetime import datetime, timedelta

import debug
from data import status
from data.config.color import Color
from data.config.layout import Layout
from data.time_formats import TIME_FORMAT_12H, TIME_FORMAT_24H, os_datetime_format
from utils import deep_update

SCROLLING_SPEEDS = [0.3, 0.2, 0.1, 0.075, 0.05, 0.025, 0.01]
DEFAULT_SCROLLING_SPEED = 2
DEFAULT_ROTATE_RATE = 15.0
MINIMUM_ROTATE_RATE = 2.0
DEFAULT_ROTATE_RATES = {"live": DEFAULT_ROTATE_RATE, "final": DEFAULT_ROTATE_RATE, "pregame": DEFAULT_ROTATE_RATE}
DEFAULT_PREFERRED_TEAMS = ["Cubs"]
DEFAULT_PREFERRED_DIVISIONS = ["NL Central"]


class Config:
    def __init__(self, filename_base, width, height):
        json = self.__get_config(filename_base)

        # Preferred Teams/Divisions
        self.preferred_teams = json["preferred"]["teams"]
        self.preferred_divisions = json["preferred"]["divisions"]

        # News Ticker
        self.news_ticker_team_offday = json["news_ticker"]["team_offday"]
        self.news_ticker_always_display = json["news_ticker"]["always_display"]
        self.news_ticker_preferred_teams = json["news_ticker"]["preferred_teams"]
        self.news_ticker_traderumors = json["news_ticker"]["traderumors"]
        self.news_ticker_mlb_news = json["news_ticker"]["mlb_news"]
        self.news_ticker_countdowns = json["news_ticker"]["countdowns"]
        self.news_ticker_date = json["news_ticker"]["date"]
        self.news_ticker_date_format = os_datetime_format(json["news_ticker"]["date_format"])
        self.news_no_games = json["news_ticker"]["display_no_games_live"]

        # Display Standings
        self.standings_team_offday = json["standings"]["team_offday"]
        self.standings_mlb_offday = json["standings"]["mlb_offday"]
        self.standings_always_display = json["standings"]["always_display"]
        self.standings_display_offday = False
        self.standings_no_games = json["standings"]["display_no_games_live"]

        # Rotation
        self.rotation_enabled = json["rotation"]["enabled"]
        self.rotation_scroll_until_finished = json["rotation"]["scroll_until_finished"]
        self.rotation_only_preferred = json["rotation"]["only_preferred"]
        self.rotation_only_live = json["rotation"]["only_live"]
        self.rotation_rates = json["rotation"]["rates"]
        self.rotation_preferred_team_live_enabled = json["rotation"]["while_preferred_team_live"]["enabled"]
        self.rotation_preferred_team_live_mid_inning = json["rotation"]["while_preferred_team_live"][
            "during_inning_breaks"
        ]

        # Weather
        self.weather_apikey = json["weather"]["apikey"]
        self.weather_location = json["weather"]["location"]
        self.weather_metric_units = json["weather"]["metric_units"]
        self.pregame_weather = json["weather"]["pregame"]

        # Misc config options
        self.time_format = json["time_format"]
        self.end_of_day = json["end_of_day"]
        self.sync_delay_seconds = json["sync_delay_seconds"]
        self.api_refresh_rate = json["api_refresh_rate"]

        self.debug = json["debug"]
        self.demo_date = json["demo_date"]
        # Make sure the scrolling speed setting is in range so we don't crash
        try:
            self.scrolling_speed = SCROLLING_SPEEDS[json["scrolling_speed"]]
        except IndexError:
            debug.warning(
                "Scrolling speed should be an integer between 0 and 6. Using default value of {}".format(
                    DEFAULT_SCROLLING_SPEED
                )
            )
            self.scrolling_speed = SCROLLING_SPEEDS[DEFAULT_SCROLLING_SPEED]

        # Get the layout info
        json = self.__get_layout(width, height)
        self.layout = Layout(json, width, height)

        # Store color information
        json = self.__get_colors("teams")
        self.team_colors = Color(json)
        json = self.__get_colors("scoreboard")
        self.scoreboard_colors = Color(json)

        # Check the preferred teams and divisions are a list or a string
        self.check_time_format()
        self.check_preferred_teams()
        self.check_preferred_divisions()

        # Check the rotation_rates to make sure it's valid and not silly
        self.check_rotate_rates()
        self.check_delay()
        self.check_api_refresh_rate()

        # Set up update delay parameter
        self.sync_rate = self.sync_delay_seconds / self.api_refresh_rate

    def check_preferred_teams(self):
        if not isinstance(self.preferred_teams, str) and not isinstance(self.preferred_teams, list):
            debug.warning(
                "preferred_teams should be an array of team names or a single team name string."
                "Using default preferred_teams, {}".format(DEFAULT_PREFERRED_TEAMS)
            )
            self.preferred_teams = DEFAULT_PREFERRED_TEAMS
        if isinstance(self.preferred_teams, str):
            team = self.preferred_teams
            self.preferred_teams = [team]

    def check_delay(self):
        if self.sync_delay_seconds < 0:
            debug.warning(
                "sync_delay_seconds should be a positive integer. Using default value of 0"
            )
            self.sync_delay_seconds = 0
        if self.sync_delay_seconds != int(self.sync_delay_seconds):
            debug.warning(
                "sync_delay_seconds should be an integer."
                f" Truncating to {int(self.sync_delay_seconds)}"
            )
            self.sync_delay_seconds = int(self.sync_delay_seconds)

    def check_api_refresh_rate(self):
        if self.api_refresh_rate < 3:
            debug.warning(
                "api_refresh_rate should be a positive integer greater than 2. Using default value of 10"
            )
            self.api_refresh_rate = 10
        if self.api_refresh_rate != int(self.api_refresh_rate):
            debug.warning(
                "api_refresh_rate should be an integer."
                f" Truncating to {int(self.api_refresh_rate)}"
            )
            self.api_refresh_rate = int(self.api_refresh_rate)

    def check_preferred_divisions(self):
        if not isinstance(self.preferred_divisions, str) and not isinstance(self.preferred_divisions, list):
            debug.warning(
                "preferred_divisions should be an array of division names or a single division name string."
                "Using default preferred_divisions, {}".format(DEFAULT_PREFERRED_DIVISIONS)
            )
            self.preferred_divisions = DEFAULT_PREFERRED_DIVISIONS
        if isinstance(self.preferred_divisions, str):
            division = self.preferred_divisions
            self.preferred_divisions = [division]

    def check_time_format(self):
        if self.time_format.lower() == "24h":
            self.time_format = TIME_FORMAT_24H
        else:
            self.time_format = TIME_FORMAT_12H

    def check_rotate_rates(self):
        for key, value in list(self.rotation_rates.items()):
            try:
                # Try and cast whatever the user passed into a float
                rate = float(value)
                self.rotation_rates[key] = rate
            except:
                # Use the default rotate rate if it fails
                debug.warning(
                    'Unable to convert rotate_rates["{}"] to a Float. Using default value. ({})'.format(
                        key, DEFAULT_ROTATE_RATE
                    )
                )
                self.rotation_rates[key] = DEFAULT_ROTATE_RATE

            if self.rotation_rates[key] < MINIMUM_ROTATE_RATE:
                debug.warning(
                    'rotate_rates["{}"] is too low. Please set it greater than {}. Using default value. ({})'.format(
                        key, MINIMUM_ROTATE_RATE, DEFAULT_ROTATE_RATE
                    )
                )
                self.rotation_rates[key] = DEFAULT_ROTATE_RATE

        # Setup some nice attributes to make sure they all exist
        self.rotation_rates_live = self.rotation_rates.get("live", DEFAULT_ROTATE_RATES["live"])
        self.rotation_rates_final = self.rotation_rates.get("final", DEFAULT_ROTATE_RATES["final"])
        self.rotation_rates_pregame = self.rotation_rates.get("pregame", DEFAULT_ROTATE_RATES["pregame"])

    def rotate_rate_for_status(self, game_status):
        rotate_rate = self.rotation_rates_live
        if status.is_pregame(game_status):
            rotate_rate = self.rotation_rates_pregame
        if status.is_complete(game_status):
            rotate_rate = self.rotation_rates_final
        return rotate_rate

    def parse_today(self):
        if self.demo_date:
            today = datetime.strptime(self.demo_date, "%Y-%m-%d")
        else:
            today = datetime.today()
            end_of_day = datetime.strptime(self.end_of_day, "%H:%M").replace(
                year=today.year, month=today.month, day=today.day
            )
            if end_of_day > datetime.now():
                today -= timedelta(days=1)
        return today.date()

    def read_json(self, path):
        """
        Read a file expected to contain valid json.
        If file not present return empty data.
        Exception if json invalid.
        """
        j = {}
        if os.path.isfile(path):
            j = json.load(open(path))
        else:
            debug.info(f"Could not find json file {path}.  Skipping.")
        return j

    # example config is a "base config" which always gets read.
    # our "custom" config contains overrides.
    def __get_config(self, base_filename):
        filename = "{}.json".format(base_filename)
        reference_filename = "config.example.json"  # always use this filename.
        reference_config = self.read_json(reference_filename)
        custom_config = self.read_json(filename)
        if custom_config:
            new_config = deep_update(reference_config, custom_config)
            return new_config
        return reference_config

    def __get_colors(self, base_filename):
        filename_prefix = "colors/{}".format(base_filename)
        filename = "{}.json".format(filename_prefix)
        reference_filename = "{}.example.json".format(filename_prefix)
        reference_colors = self.read_json(reference_filename)
        if not reference_colors:
            debug.error(
                "Invalid {} reference color file. Make sure {} exists in colors/".format(base_filename, base_filename)
            )
            sys.exit(1)

        custom_colors = self.read_json(filename)
        if custom_colors:
            debug.info("Custom '%s.json' colors found. Merging with default reference colors.", base_filename)
            new_colors = deep_update(reference_colors, custom_colors)
            return new_colors
        return reference_colors

    def __get_layout(self, width, height):
        filename_prefix = "coordinates/w{}h{}".format(width, height)
        filename = "{}.json".format(filename_prefix)
        reference_filename = "{}.example.json".format(filename_prefix)
        reference_layout = self.read_json(reference_filename)
        if not reference_layout:
            # Unsupported coordinates
            debug.error(
                "Invalid matrix dimensions provided. See top of README for supported dimensions."
                "\nIf you would like to see new dimensions supported, please file an issue on GitHub!"
            )
            sys.exit(1)

        # Load and merge any layout customizations
        custom_layout = self.read_json(filename)
        if custom_layout:
            debug.info("Custom '%dx%d.json' found. Merging with default reference layout.", width, height)
            new_layout = deep_update(reference_layout, custom_layout)
            return new_layout
        return reference_layout
