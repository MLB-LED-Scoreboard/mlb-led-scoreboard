import os, sys

from utils import logger as ScoreboardLogger
from utils.font import FontCache
from utils import deep_update, read_json, value_at_keypath

from collections import namedtuple


class Layout:
    class LayoutNotFound(Exception):
        pass

    LAYOUT_DIRECTORY = os.path.abspath(os.path.join(__file__, "../../coordinates"))
    FONTNAME_DEFAULT = "4x6"
    FONTNAME_KEY = "font_name"

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font_cache = FontCache(self.FONTNAME_DEFAULT)

        self._json = self.__fetch_layout()

    def coords(self, keypath):
        try:
            coord_dict = value_at_keypath(self._json, keypath)
        except KeyError as e:
            raise e

        if not isinstance(coord_dict, dict):  # or not self.state in Layout.AVAILABLE_OPTIONAL_KEYS:
            return coord_dict

        # TODO: Handle state
        # if self.state in coord_dict:
        #     return coord_dict[self.state]

        coord_constructor = namedtuple("Coords", coord_dict.keys())

        return coord_constructor(**coord_dict)

    def font(self, font_name):
        """
        Fetches a font from the font cache.
        """
        return (self.font_cache.fetch_font(font_name), self.font_size(font_name))

    def font_for(self, keypath):
        font = value_at_keypath(self._json, keypath)
        font_name = font.get(Layout.FONTNAME_KEY, Layout.FONTNAME_DEFAULT)

        return self.font(font_name)

    def font_size(self, font_name):
        return self.font_cache.font_size(font_name)

    def __fetch_layout(self):
        filename = os.path.join(Layout.LAYOUT_DIRECTORY, f"w{self.width}h{self.height}.json")
        reference_filename = os.path.join(Layout.LAYOUT_DIRECTORY, f"{filename}.example")
        reference_layout = read_json(reference_filename)
        if not reference_layout:
            # Unsupported coordinates
            ScoreboardLogger.error(
                "Invalid matrix dimensions provided. See top of README for supported dimensions."
                "\nIf you would like to see new dimensions supported, please file an issue on GitHub!"
            )
            sys.exit(1)

        # Load and merge any layout customizations
        custom_layout = read_json(filename)
        if custom_layout:
            ScoreboardLogger.info(
                "Custom '%dx%d.json' found. Merging with default reference layout.", self.width, self.height
            )
            layout = deep_update(reference_layout, custom_layout)

            return layout

        return reference_layout
