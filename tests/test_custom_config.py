import json
import unittest
from pathlib import Path
from unittest import mock

from data.config import Config
from data.paths import COORDINATES_DIRECTORY, COLORS_DIRECTORY


FIXTURES = Path(__file__).parent / "fixtures"
CUSTOM_CONFIG_PATH = FIXTURES / "config.json"

def make_config(config_path="nonexistent", use_layout=False, use_teams=False, use_scoreboard=False):
    """
    Instantiate a real Config, optionally redirecting custom layout/color reads to
    fixture files. Config reads custom layout/color files by bare filename (e.g.
    "w32h32.json") relative to CWD, so we intercept those specific reads and
    redirect them to tests/fixtures/.
    """
    redirects = {}
    if use_layout:
        redirects[COORDINATES_DIRECTORY / "w32h32.json"] = FIXTURES / "coordinates" / "w32h32.json"
    if use_teams:
        redirects[COLORS_DIRECTORY / "teams.json"] = FIXTURES / "colors" / "teams.json"
    if use_scoreboard:
        redirects[COLORS_DIRECTORY / "scoreboard.json"] = FIXTURES / "colors" / "scoreboard.json"

    original_read_json = Config.read_json

    def patched_read_json(self, path):
        path = Path(str(path))
        if path in redirects:
            path = redirects[path]
        return original_read_json(self, path)

    # Patch reads, patch warning on missing files
    with mock.patch.object(Config, "read_json", patched_read_json), mock.patch("debug.warning"):
        return Config(config_path, 32, 32)


def flatten(d, prefix=""):
    """Recursively yield (dotted_keypath, value) for every leaf in a nested dict."""
    for key, value in d.items():
        keypath = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            yield from flatten(value, keypath)
        else:
            yield keypath, value

class TestCustomConfig(unittest.TestCase):
    """Custom config.json overrides are applied on top of config.example.json defaults."""

    @classmethod
    def setUpClass(cls):
        cls.default_config = make_config()
        cls.custom_config = make_config(CUSTOM_CONFIG_PATH)

    def test_custom_not_present(self):
        no_custom = make_config()
        self.assertEqual(no_custom, self.default_config)

    def test_custom_config_priority(self):
        self.assertNotEqual(self.custom_config, self.default_config)

    def test_custom_preferred_teams_override(self):
        self.assertEqual(self.custom_config.preferred_teams, ["Braves"])
        self.assertNotEqual(self.custom_config.preferred_teams, self.default_config.preferred_teams)

    def test_custom_preferred_divisions_override(self):
        self.assertEqual(self.custom_config.preferred_divisions, ["AL Central", "AL Wild Card"])
        self.assertNotEqual(self.custom_config.preferred_divisions, self.default_config.preferred_divisions)

    def test_custom_debug_override(self):
        self.assertTrue(self.custom_config.debug)
        self.assertNotEqual(self.custom_config.debug, self.default_config.debug)

    def test_custom_weather_location_override(self):
        self.assertEqual(self.custom_config.weather_location, "New York,ny,us")
        self.assertNotEqual(self.custom_config.weather_location, self.default_config.weather_location)

    def test_custom_rotation_rates_override(self):
        self.assertEqual(self.custom_config.rotation_rates_live, 20.0)
        self.assertEqual(self.custom_config.rotation_rates_final, 20.0)
        self.assertEqual(self.custom_config.rotation_rates_pregame, 20.0)
        self.assertNotEqual(self.custom_config.rotation_rates_live, self.default_config.rotation_rates_live)

    def test_custom_scrolling_speed_override(self):
        from data.config import SCROLLING_SPEEDS
        self.assertEqual(self.custom_config.scrolling_speed, SCROLLING_SPEEDS[1])
        self.assertNotEqual(self.custom_config.scrolling_speed, self.default_config.scrolling_speed)

    def test_custom_time_format_override(self):
        from data.time_formats import TIME_FORMAT_24H
        self.assertEqual(self.custom_config.time_format, TIME_FORMAT_24H)
        self.assertNotEqual(self.custom_config.time_format, self.default_config.time_format)

    def test_unset_keys_equal_default(self):
        self.assertEqual(self.custom_config.preferred_game_delay_multiplier, self.default_config.preferred_game_delay_multiplier)
        self.assertEqual(self.custom_config.api_refresh_rate, self.default_config.api_refresh_rate)


class TestCustomLayout(unittest.TestCase):
    """Custom coordinate JSON is applied on top of the example layout defaults."""

    @classmethod
    def setUpClass(cls):
        cls.default_config = make_config()
        cls.custom_config = make_config(CUSTOM_CONFIG_PATH, use_layout=True)

    def test_custom_not_present(self):
        no_custom = make_config(CUSTOM_CONFIG_PATH)
        self.assertEqual(no_custom.layout, self.default_config.layout)

    def test_custom_config_priority(self):
        self.assertNotEqual(self.custom_config.layout, self.default_config.layout)

    def test_custom_config_values(self):
        with open(FIXTURES / "coordinates" / "w32h32.json") as f:
            fixture = json.load(f)
        for keypath, expected in flatten(fixture):
            if keypath.startswith("_"):
                continue
            actual = self.custom_config.layout.json
            for part in keypath.split("."):
                actual = actual[part]
            self.assertEqual(actual, expected, f"mismatch at {keypath}")


class TestCustomTeamColors(unittest.TestCase):
    """Custom teams.json color values are applied on top of teams.example.json defaults."""

    @classmethod
    def setUpClass(cls):
        cls.default_config = make_config()
        cls.custom_config = make_config(CUSTOM_CONFIG_PATH, use_teams=True)

    def test_custom_not_present(self):
        no_custom = make_config(CUSTOM_CONFIG_PATH)
        self.assertEqual(no_custom.team_colors, self.default_config.team_colors)

    def test_custom_config_priority(self):
        self.assertNotEqual(self.custom_config.team_colors, self.default_config.team_colors)

    def test_custom_config_values(self):
        expected = {"r": 1, "g": 2, "b": 3}
        for keypath, value in flatten(self.custom_config.team_colors.json):
            if keypath.startswith("_"):
                continue
            channel = keypath.rsplit(".", 1)[-1]
            if channel in expected:
                self.assertEqual(value, expected[channel], f"expected {channel}={expected[channel]} at {keypath}")


class TestCustomScoreboardColors(unittest.TestCase):
    """Custom scoreboard.json color values are applied on top of scoreboard.example.json defaults."""

    @classmethod
    def setUpClass(cls):
        cls.default_config = make_config()
        cls.custom_config = make_config(CUSTOM_CONFIG_PATH, use_scoreboard=True)

    def test_custom_not_present(self):
        no_custom = make_config(CUSTOM_CONFIG_PATH)
        self.assertEqual(no_custom.scoreboard_colors, self.default_config.scoreboard_colors)

    def test_custom_config_priority(self):
        self.assertNotEqual(self.custom_config.scoreboard_colors, self.default_config.scoreboard_colors)

    def test_custom_config_values(self):
        expected = {"r": 1, "g": 2, "b": 3}
        for keypath, value in flatten(self.custom_config.scoreboard_colors.json):
            if keypath.startswith("_"):
                continue
            if keypath.endswith((".r", ".g", ".b")):
                channel = keypath.rsplit(".", 1)[-1]
                self.assertEqual(value, expected[channel], f"expected {channel}={expected[channel]} at {keypath}")


if __name__ == "__main__":
    unittest.main()
