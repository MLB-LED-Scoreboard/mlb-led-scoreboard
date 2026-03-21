import json
import os
import sys

from datetime import datetime, time, timedelta
from enum import Enum
from collections import defaultdict
from typing import Mapping, Optional
from math import ceil

import debug
from data import status
from data.config.color import Color
from data.config.layout import Layout
from data import teams as team_metadata
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

        # Preferred Teams/Divisions

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
        if not isinstance(other, Config):
            return NotImplemented
        return vars(self) == vars(other)


class Requirements(Enum):
    LIVE = "live"
    LIVE_IN_INNING = "live_in_inning"
    PREGAME = "pregame"
    GAME_OVER = "game_over"

    def __str__(self):
        return self.value

    @staticmethod
    def from_str(label):
        for requirement in Requirements:
            if requirement.value == label:
                return requirement
        raise ValueError(f"Unknown requirement: {label}")


class GameRule:
    DEFAULT_PRIORITY = 0, True

    def __init__(
        self,
        priority: int,
        *,
        requirement: Optional[Requirements] = None,
        passive=False,
        teams: list[str] = [],
    ):
        self.requirement = requirement
        self.when_matched = priority, passive
        self.teams = set(team_metadata.get_team_id(t) for t in teams)

    def priority(self) -> int:
        return self.when_matched[0]

    def matches(self, game) -> tuple[int, bool]:
        if self.teams and not set([game["away_id"], game["home_id"]]).intersection(self.teams):
            return GameRule.DEFAULT_PRIORITY

        if self.requirement is None:
            return self.when_matched

        if self.requirement == Requirements.PREGAME and status.is_pregame(game["status"]):
            return self.when_matched

        if self.requirement == Requirements.GAME_OVER and status.is_complete(game["status"]):
            return self.when_matched

        if self.requirement == Requirements.LIVE and (
            status.is_fresh(game["status"]) or (status.is_live(game["status"]))
        ):
            return self.when_matched

        if self.requirement == Requirements.LIVE_IN_INNING and (
            status.is_live(game["status"])
            and game["status"] != status.WARMUP
            and not status.is_inning_break(game["inning_state"])
        ):
            return self.when_matched

        return GameRule.DEFAULT_PRIORITY

    def __repr__(self):
        return (
            f"GameRule(priority={self.when_matched[0]}, requirement={self.requirement}"
            f", passive={self.when_matched[1]}, teams={self.teams})"
        )

    def __eq__(self, other):
        if not isinstance(other, GameRule):
            return NotImplemented
        return (
            self.requirement == other.requirement
            and self.when_matched == other.when_matched
            and self.teams == other.teams
        )


class TimeRule:
    # TODO(bmw): extend to day of week?
    def __init__(
        self,
        priority: int,
        *,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
    ):
        self.priority = priority
        self.start_time = start_time
        self.end_time = end_time

    def matches(self, now: time) -> int:
        if self.start_time and now < self.start_time:
            return 0
        if self.end_time and now > self.end_time:
            return 0
        return self.priority

    def __repr__(self):
        return f"TimeRule(priority={self.priority}, start_time={self.start_time}, end_time={self.end_time})"

    def __eq__(self, other):
        if not isinstance(other, TimeRule):
            return NotImplemented
        return (
            self.priority == other.priority
            and self.start_time == other.start_time
            and self.end_time == other.end_time
        )

def _parse_requirements(json) -> Optional[Requirements]:
    json_requirement = json.get("required_status")
    if json_requirement:
        try:
            return Requirements.from_str(json_requirement)
        except ValueError:
            raise ValueError(
                "Invalid game rule in config, unknown required_status '{}'. Rule: {}".format(json_requirement, json)
            )
    return None


def _parse_with_priority(json) -> list[int]:
    with_priority = json.get("with_priority")
    if with_priority is None:
        raise ValueError("Invalid screen rule in config, missing 'with_priority' field. Rule: {}".format(json))

    if isinstance(with_priority, int):
        return [with_priority]
    elif isinstance(with_priority, list) and all(isinstance(p, int) for p in with_priority):
        return with_priority
    else:
        raise ValueError(
            "Invalid screen rule in config, 'with_priority' field should be an integer or list of integers. Rule: {}".format(
                json
            )
        )


VALID_NON_GAME_SCREEN_TYPES = ["news", "standings"]


def _screen_rules_from_json(json) -> tuple[list[GameRule], list[TimeRule], Mapping[str, Mapping[int, int]]]:
    game_rules = []
    time_rules = []
    screen_rules: defaultdict[str, defaultdict[int, int]] = defaultdict(lambda: defaultdict(int))

    for rule_json in json:
        if "kind" not in rule_json:
            raise ValueError("Invalid rule in config, missing 'kind' field. Rule: {}".format(rule_json))

        if rule_json["kind"] == "game":
            if "priority" not in rule_json:
                raise ValueError("Invalid game rule in config, missing 'priority' field. Rule: {}".format(rule_json))
            rule = GameRule(
                priority=rule_json["priority"],
                requirement=_parse_requirements(rule_json),
                passive=False,
                teams=rule_json.get("teams", []),
            )
            game_rules.append(rule)
        elif rule_json["kind"] == "secondary_game":
            requirement = _parse_requirements(rule_json)
            for priority in _parse_with_priority(rule_json):
                rule = GameRule(
                    priority=priority,
                    requirement=requirement,
                    passive=True,
                    teams=rule_json.get("teams", []),
                )
                game_rules.append(rule)
        elif rule_json["kind"] == "time":
            if "priority" not in rule_json:
                raise ValueError("Invalid time rule in config, missing 'priority' field. Rule: {}".format(rule_json))
            start_time = None
            end_time = None
            if "start_time" in rule_json:
                try:
                    start_time = datetime.strptime(rule_json["start_time"], "%H:%M").time()
                except ValueError:
                    raise ValueError(
                        "Invalid time format for 'start_time' in config. Expected HH:MM. Rule: {}".format(rule_json)
                    )
            if "end_time" in rule_json:
                try:
                    end_time = datetime.strptime(rule_json["end_time"], "%H:%M").time()
                except ValueError:
                    raise ValueError(
                        "Invalid time format for 'end_time' in config. Expected HH:MM. Rule: {}".format(rule_json)
                    )
            if start_time is None and end_time is None:
                raise ValueError(
                    "Invalid time rule in config, need at least one of 'start_time' or 'end_time' fields. Rule: {}".format(
                        rule_json
                    )
                )
            time_rules.append(TimeRule(priority=rule_json["priority"], start_time=start_time, end_time=end_time))

        elif rule_json["kind"] in VALID_NON_GAME_SCREEN_TYPES:
            if "seconds" not in rule_json:
                raise ValueError("Invalid screen rule in config, missing 'seconds' field. Rule: {}".format(rule_json))
            for priority in _parse_with_priority(rule_json):
                screen_rules[rule_json["kind"]][priority] = rule_json["seconds"]
        else:
            debug.warning(
                "Invalid screen rule in config, unknown type '{}'. Skipping. Rule: {}".format(
                    rule_json.get("kind"), rule_json
                )
            )

    if not any(screen_rules[s][0] for s in screen_rules.keys()):
        # prevents nothing showing for an empty config
        screen_rules["news"][0] = 60

    return game_rules, time_rules, screen_rules
