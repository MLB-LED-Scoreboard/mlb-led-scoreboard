import os, sys

from utils import logger as ScoreboardLogger
from utils import deep_update, read_json


class Colors:
    COLORS_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../colors"))

    TEAM_COLORS_REFERENCE_FILENAME = "teams.json.example"
    SCOREBOARD_COLORS_REFERENCE_FILENAME = "scoreboard.json.example"

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
