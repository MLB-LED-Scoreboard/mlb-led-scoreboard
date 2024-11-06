import os, sys

from utils import logger as ScoreboardLogger
from utils import value_at_keypath, deep_update, read_json


class Colors:
    COLORS_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../colors"))

    TEAM_COLORS_REFERENCE_FILENAME = "teams.json.example"
    SCOREBOARD_COLORS_REFERENCE_FILENAME = "scoreboard.json.example"

    DEFAULT_COLOR = (0, 0, 0)

    def __init__(self):
        self._team_json = self.__fetch_colors(Colors.TEAM_COLORS_REFERENCE_FILENAME)
        self._scoreboard_json = self.__fetch_colors(Colors.SCOREBOARD_COLORS_REFERENCE_FILENAME)

    def __fetch_colors(self, reference_filename):
        filename = reference_filename.strip(".example")
        reference_colors = read_json(os.path.join(Colors.COLORS_DIRECTORY, reference_filename))
        if not reference_colors:
            ScoreboardLogger.error(
                "Invalid {} reference color file. Make sure {} exists in colors/".format(filename, filename)
            )
            sys.exit(1)

        custom_colors = read_json(os.path.join(Colors.COLORS_DIRECTORY, filename))
        if custom_colors:
            ScoreboardLogger.info("Custom '%s.json' colors found. Merging with default reference colors.", filename)
            colors = deep_update(reference_colors, custom_colors)

            return colors

        return reference_colors

    def team_graphics_color(self, keypath, default=True):
        return self.__fetch_color(self._team_json, keypath, default)

    def graphics_color(self, keypath, default=True):
        return self.__fetch_color(self._scoreboard_json, keypath, default)

    def __fetch_color(self, config, keypath, default):
        color = value_at_keypath(config, keypath)

        if color:
            return (color["r"], color["g"], color["b"])

        if default:
            return Colors.DEFAULT_COLOR

        return None
