import json
import os
import sys

from datetime import datetime, timedelta
from collections import defaultdict, namedtuple
from typing import Mapping
from math import ceil

from bullpen.api.config import MLBConfig
from bullpen.util import deep_update
from bullpen.time_formats import TIME_FORMAT_12H, TIME_FORMAT_24H
import statsapi

from data.config.game_screen import GameScreen, parse_game_screen
from data.config.other_screens import TimeRule, parse_time_rule, parse_with_priority
from bullpen.logging import LOGGER
from data import status
from data.config.color import Color
from data.config.layout import Layout
from data.paths import *
import cli
from driver import RGBMatrixOptions

SCROLLING_SPEEDS = [0.3, 0.2, 0.1, 0.075, 0.05, 0.025, 0.01]
DEFAULT_SCROLLING_SPEED = 2
DEFAULT_ROTATE_RATE = 15.0
MINIMUM_ROTATE_RATE = 2.0
DEFAULT_ROTATE_RATES = {"live": DEFAULT_ROTATE_RATE, "final": DEFAULT_ROTATE_RATE, "pregame": DEFAULT_ROTATE_RATE}


ConfigForPlugin = namedtuple(
    "ConfigForPlugin",
    ["scrolling_speed", "time_format", "plugin_config", "parse_today", "is_postseason"],
)


class Config:
    def __init__(self):
        args = cli.arguments()

        self.config_path = args.config
        self.emulated = args.emulated

        json = self.__get_config(self.config_path)

        # Matrix options (merged with CLI args)
        self.matrix_options = self.__matrix_options(json['matrix'])

        # Rotation
        self.rotation_scroll_until_finished = json["rotation"]["scroll_until_finished"]
        self.rotation_rates = json["rotation"]["rates"]

        self.rotation_game_rules, self.rotation_time_rules, self.rotation_screen_rules = _screen_rules_from_json(
            json["rotation"]["screens"]
        )

        # TODO moving this inside a 'plugin' is a bit weird?
        self.pregame_weather = json["weather"]["pregame"]

        # Misc config options
        self.time_format = json["time_format"]
        self.end_of_day = json["end_of_day"]
        self.sync_delay_seconds = json["sync_delay_seconds"]
        self.api_refresh_rate = json["api_refresh_rate"]

        self.debug = json["debug"]
        self.demo_date = json["demo_date"]

        self.playoffs_start_date = _get_playoff_start_date(self.parse_today().year)

        # Make sure the scrolling speed setting is in range so we don't crash
        try:
            self.scrolling_speed = SCROLLING_SPEEDS[json["scrolling_speed"]]
        except IndexError:
            LOGGER.warning(
                "Scrolling speed should be an integer between 0 and 6. Using default value of {}".format(
                    DEFAULT_SCROLLING_SPEED
                )
            )
            self.scrolling_speed = SCROLLING_SPEEDS[DEFAULT_SCROLLING_SPEED]

        self.standings_json = json.get("standings", {})
        self.news_json = json.get("news_ticker", {}) | json.get("weather")
        self.plugin_json = json.get("plugins", {})

        # Get the layout info
        width = self.matrix_options.cols
        height = self.matrix_options.rows
        json = self.__get_layout(width, height)
        self.layout = Layout(json, width, height)

        # Store color information
        json = self.__get_colors("teams")
        self.team_colors = Color(json)
        json = self.__get_colors("scoreboard")
        self.scoreboard_colors = Color(json)

        # Check the preferred teams and divisions are a list or a string
        self.check_time_format()

        # Check the rotation_rates to make sure it's valid and not silly
        self.check_rotate_rates()
        self.check_delay()
        self.check_api_refresh_rate()

        # Set up update delay parameter
        self.sync_amount = ceil(self.sync_delay_seconds / self.api_refresh_rate)

    def check_delay(self):
        if self.sync_delay_seconds < 0:
            LOGGER.warning("sync_delay_seconds should be a positive integer. Using default value of 0")
            self.sync_delay_seconds = 0
        if self.sync_delay_seconds != int(self.sync_delay_seconds):
            LOGGER.warning("sync_delay_seconds should be an integer." f" Truncating to {int(self.sync_delay_seconds)}")
            self.sync_delay_seconds = int(self.sync_delay_seconds)

    def check_api_refresh_rate(self):
        if self.api_refresh_rate < 3:
            LOGGER.warning("api_refresh_rate should be a positive integer greater than 2. Using default value of 10")
            self.api_refresh_rate = 10
        if self.api_refresh_rate != int(self.api_refresh_rate):
            LOGGER.warning("api_refresh_rate should be an integer." f" Truncating to {int(self.api_refresh_rate)}")
            self.api_refresh_rate = int(self.api_refresh_rate)

    def check_screens(self, plugins: list[str]):
        for level in self.rotation_screen_rules.values():
            for screen in level:
                if screen not in plugins:
                    raise ValueError(
                        f"Screen with 'kind': '{screen}' in config does not have a corresponding plugin. Please add a plugin for this screen or remove it from the config."
                    )

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
                LOGGER.warning(
                    'Unable to convert rotate_rates["{}"] to a Float. Using default value. ({})'.format(
                        key, DEFAULT_ROTATE_RATE
                    )
                )
                self.rotation_rates[key] = DEFAULT_ROTATE_RATE

            if self.rotation_rates[key] < MINIMUM_ROTATE_RATE:
                LOGGER.warning(
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

    def is_postseason(self):
        return self.parse_today() > self.playoffs_start_date

    def screen_time_at_priority(self, screen: str, priority: int) -> int:
        return self.rotation_screen_rules.get(priority, {}).get(screen, 0)

    def for_plugin(self, plugin_name: str) -> MLBConfig:

        match plugin_name:
            case "news":
                # for legacy reasons, we let this plugin have two separate config names
                plugin_config = self.news_json
            case "standings":
                plugin_config = self.standings_json
            case _:
                plugin_config = self.plugin_json.get(plugin_name, {})

        return ConfigForPlugin(
            self.scrolling_speed, self.time_format, plugin_config, self.parse_today, self.is_postseason
        )

    def read_json(self, path):
        """
        Read a file expected to contain valid json.
        If file not present return empty data.
        Exception if json invalid.
        """
        if not os.path.isfile(path):
            LOGGER.warning("Config file %s not found. Using default values for this file.", path)
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
            LOGGER.critical(
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
                LOGGER.error(
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
            LOGGER.critical(
                f"""\
Invalid reference color file. Make sure {reference_filename} exists in colors/.
You should not edit or move this file!"
"""
            )
            sys.exit(1)

        custom_colors = self.read_json(filename)
        if custom_colors:
            LOGGER.info("Custom '%s.json' colors found. Merging with default reference colors.", base_filename)
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
            LOGGER.critical(
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
            LOGGER.info("Custom '%dx%d.json' found. Merging with default reference layout.", width, height)
            new_layout = deep_update(reference_layout, custom_layout)
            return new_layout
        return reference_layout
    
    def __matrix_options(self, overrides):
        args = cli.arguments(overrides=overrides)

        self.emulated = args.emulated

        options = RGBMatrixOptions()

        if args.led_gpio_mapping is not None:
            options.hardware_mapping = args.led_gpio_mapping

        options.rows = args.led_rows
        options.cols = args.led_cols
        options.chain_length = args.led_chain
        options.parallel = args.led_parallel
        options.row_address_type = args.led_row_addr_type
        options.multiplexing = args.led_multiplexing
        options.pwm_bits = args.led_pwm_bits
        options.brightness = args.led_brightness
        options.scan_mode = args.led_scan_mode
        options.pwm_lsb_nanoseconds = args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = args.led_rgb_sequence
        options.drop_privileges = args.drop_privileges

        try:
            options.pixel_mapper_config = args.led_pixel_mapper
        except AttributeError:
            LOGGER.warning("Your compiled RGB Matrix Library is out of date.")
            LOGGER.warning("The --led-pixel-mapper argument will not work until it is updated.")

        try:
            options.pwm_dither_bits = args.led_pwm_dither_bits
        except AttributeError:
            LOGGER.warning("Your compiled RGB Matrix Library is out of date.")
            LOGGER.warning("The --led-pwm-dither-bits argument will not work until it is updated.")

        try:
            options.limit_refresh_rate_hz = args.led_limit_refresh
        except AttributeError:
            LOGGER.warning("Your compiled RGB Matrix Library is out of date.")
            LOGGER.warning("The --led-limit-refresh argument will not work until it is updated.")

        if args.led_show_refresh:
            options.show_refresh_rate = 1

        if args.led_slowdown_gpio is not None:
            options.gpio_slowdown = args.led_slowdown_gpio

        if args.led_no_hardware_pulse:
            options.disable_hardware_pulsing = True

        return options

    def __eq__(self, other):
        if not isinstance(other, Config):
            return False

        self_keys = { k: v for k, v in vars(self).items() if k != 'matrix_options' }
        other_keys = { k: v for k, v in vars(other).items() if k != 'matrix_options' }

        keys_match = self_keys == other_keys

        # Spot check matrix options. These don't need strict equality, for config we only care about size.
        options_match = self.matrix_options.cols == other.matrix_options.cols and self.matrix_options.rows == other.matrix_options.rows

        return keys_match and options_match


def _screen_rules_from_json(json) -> tuple[list[GameScreen], list[TimeRule], Mapping[int, Mapping[str, int]]]:
    game_rules = []
    time_rules = []
    screen_rules: defaultdict[int, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))

    for rule_json in json:
        if "kind" not in rule_json:
            raise ValueError("Invalid rule in config, missing 'kind' field. Rule: {}".format(rule_json))

        if rule_json["kind"] == "game" or rule_json["kind"] == "secondary_game":
            game_rules.extend(parse_game_screen(rule_json))
        elif rule_json["kind"] == "time":
            time_rules.append(parse_time_rule(rule_json))
        else:
            if "seconds" not in rule_json:
                raise ValueError("Invalid screen rule in config, missing 'seconds' field. Rule: {}".format(rule_json))
            for priority in parse_with_priority(rule_json):
                screen_rules[priority][rule_json["kind"]] = rule_json["seconds"]

    if not len(screen_rules[0]):
        raise ValueError(
            "Invalid screens config! Add at least one with with 'with_priority=0' for when no games are available."
        )

    for t in time_rules:
        has_matching_screen = False
        for screen_rule in screen_rules[t.priority].values():
            if screen_rule > 0:
                has_matching_screen = True
                break
        if not has_matching_screen:
            raise ValueError(
                "Invalid time rule in screens config, can lead to situation with no valid screens."
                f" Remove this rule or add at least one with with 'with_priority={t.priority}'."
            )

    return game_rules, time_rules, screen_rules


def _get_playoff_start_date(year: int):
    try:
        dates = statsapi.get("season", {"sportId": 1, "seasonId": year})["seasons"][0]
        return datetime.strptime(dates["regularSeasonEndDate"], "%Y-%m-%d").date()
    except Exception:
        LOGGER.exception("Failed to get season data, defaulting playoff start date to Oct 1")

    return datetime(year, 10, 1).date()
