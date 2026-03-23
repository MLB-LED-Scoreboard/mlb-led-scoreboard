import json
import os
import sys

from datetime import datetime, timedelta
from collections import defaultdict
from typing import Mapping
from math import ceil

from data.config.game_screen import GameScreen, parse_game_screen
from data.config.other_screens import VALID_NON_GAME_SCREEN_TYPES, TimeRule, parse_time_rule, parse_with_priority
import debug
from data import status
from data.config.color import Color
from data.config.layout import Layout
from data.paths import *
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
    def __init__(self, config_path, width, height):
        json = self.__get_config(config_path)

        # News Ticker
        self.preferred_teams = json["news_ticker"]["teams"]
        self.news_ticker_traderumors = json["news_ticker"]["traderumors"]
        self.news_ticker_mlb_news = json["news_ticker"]["mlb_news"]
        self.news_ticker_countdowns = json["news_ticker"]["countdowns"]
        self.news_ticker_date = json["news_ticker"]["date"]
        self.news_ticker_date_format = os_datetime_format(json["news_ticker"]["date_format"])

        # Display Standings
        self.preferred_divisions = json["standings"]["divisions"]

        # Rotation
        self.rotation_scroll_until_finished = json["rotation"]["scroll_until_finished"]
        self.rotation_rates = json["rotation"]["rates"]

        self.rotation_game_rules, self.rotation_time_rules, self.rotation_screen_rules = _screen_rules_from_json(
            json["rotation"]["screens"]
        )

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
        self.sync_amount = ceil(self.sync_delay_seconds / self.api_refresh_rate)

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
            debug.warning("sync_delay_seconds should be a positive integer. Using default value of 0")
            self.sync_delay_seconds = 0
        if self.sync_delay_seconds != int(self.sync_delay_seconds):
            debug.warning("sync_delay_seconds should be an integer." f" Truncating to {int(self.sync_delay_seconds)}")
            self.sync_delay_seconds = int(self.sync_delay_seconds)

    def check_api_refresh_rate(self):
        if self.api_refresh_rate < 3:
            debug.warning("api_refresh_rate should be a positive integer greater than 2. Using default value of 10")
            self.api_refresh_rate = 10
        if self.api_refresh_rate != int(self.api_refresh_rate):
            debug.warning("api_refresh_rate should be an integer." f" Truncating to {int(self.api_refresh_rate)}")
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

    def rotate_rate_for_status(self, game_status: str):
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

    def screen_time_at_priority(self, screen: str, priority: int) -> int:
        return self.rotation_screen_rules.get(screen, {}).get(priority, 0)

    def read_json(self, path):
        """
        Read a file expected to contain valid json.
        If file not present return empty data.
        Exception if json invalid.
        """
        if not os.path.isfile(path):
            debug.warning("Config file %s not found. Using default values for this file.", path)
            return {}

        with open(path) as f:
            return json.load(f)

    def __get_config(self, path=None):
        if path is None:
            path = ROOT_DIRECTORY / "config.json"
        else:
            path = (CURRENT_DIRECTORY / path).with_suffix(".json")
        reference_filename = "config.example.json"
        reference_path = ROOT_DIRECTORY / reference_filename
        reference_config = self.read_json(reference_path)
        custom_config = self.read_json(path)
        if not reference_config:
            debug.critical(
                f"""\
Invalid example configuration. Make sure {reference_filename} exists in root directory.
You should not edit or move this file!
"""
            )
            sys.exit(1)

        if custom_config:
            if "format" in reference_config and (
                "format" not in custom_config or custom_config["format"] != reference_config["format"]
            ):
                debug.error(
                    "Config format version {} does not match expected format version {}. Please update your config file.".format(
                        custom_config.get("format"), reference_config["format"]
                    )
                )
                sys.exit(1)
            new_config = deep_update(reference_config, custom_config)
            return new_config
        return reference_config

    def __get_colors(self, base_filename):
        filename = COLORS_DIRECTORY / "{}.json".format(base_filename)
        reference_filename = "{}.example.json".format(base_filename)
        reference_path = COLORS_DIRECTORY / reference_filename
        reference_colors = self.read_json(reference_path)
        if not reference_colors:
            debug.critical(
                f"""\
Invalid reference color file. Make sure {reference_filename} exists in colors/.
You should not edit or move this file!"
"""
            )
            sys.exit(1)

        custom_colors = self.read_json(filename)
        if custom_colors:
            debug.info("Custom '%s.json' colors found. Merging with default reference colors.", base_filename)
            new_colors = deep_update(reference_colors, custom_colors)
            return new_colors
        return reference_colors

    def __get_layout(self, width, height):
        filename_prefix = "w{}h{}".format(width, height)
        filename = COORDINATES_DIRECTORY / "{}.json".format(filename_prefix)
        reference_filename = "{}.example.json".format(filename_prefix)
        reference_path = COORDINATES_DIRECTORY / reference_filename
        reference_layout = self.read_json(reference_path)
        if not reference_layout:
            supported_dimensions = sorted(
                [file.name.split(".")[0] for file in COORDINATES_DIRECTORY.glob("*.example.json")], reverse=True
            )
            debug.critical(
                f"""\
Invalid reference layout file. Make sure {reference_filename} exists in coordinates/
You should not edit or move this file!

Supported dimensions are: {', '.join(supported_dimensions)}
If you aren't sure why you're seeing this, there might not be official support for your matrix dimensions yet.
"""
            )
            sys.exit(1)

        # Load and merge any layout customizations
        custom_layout = self.read_json(filename)
        if custom_layout:
            debug.info("Custom '%dx%d.json' found. Merging with default reference layout.", width, height)
            new_layout = deep_update(reference_layout, custom_layout)
            return new_layout
        return reference_layout

    def __eq__(self, other):
        return isinstance(other, Config) and vars(self) == vars(other)


def _screen_rules_from_json(json) -> tuple[list[GameScreen], list[TimeRule], Mapping[str, Mapping[int, int]]]:
    game_rules = []
    time_rules = []
    screen_rules: defaultdict[str, defaultdict[int, int]] = defaultdict(lambda: defaultdict(int))

    for rule_json in json:
        if "kind" not in rule_json:
            raise ValueError("Invalid rule in config, missing 'kind' field. Rule: {}".format(rule_json))

        if rule_json["kind"] == "game" or rule_json["kind"] == "secondary_game":
            game_rules.extend(parse_game_screen(rule_json))
        elif rule_json["kind"] == "time":
            time_rules.append(parse_time_rule(rule_json))
        elif rule_json["kind"] in VALID_NON_GAME_SCREEN_TYPES:
            if "seconds" not in rule_json:
                raise ValueError("Invalid screen rule in config, missing 'seconds' field. Rule: {}".format(rule_json))
            for priority in parse_with_priority(rule_json):
                screen_rules[rule_json["kind"]][priority] = rule_json["seconds"]
        else:
            debug.warning(
                "Invalid screen rule in config, unknown type '{}'. Skipping. Rule: {}".format(
                    rule_json.get("kind"), rule_json
                )
            )

    if not any(screen[0] for screen in screen_rules.values()):
        raise ValueError(
            "Invalid screens config! Add at least one with with 'with_priority=0' for when no games are available."
        )

    for t in time_rules:
        has_matching_screen = False
        for screen_rule in screen_rules.values():
            if screen_rule.get(t.priority, 0) > 0:
                has_matching_screen = True
                break
        if not has_matching_screen:
            raise ValueError(
                "Invalid time rule in screens config, can lead to situation with no valid screens."
                f" Remove this rule or add at least one with with 'with_priority={t.priority}'."
            )

    return game_rules, time_rules, screen_rules
