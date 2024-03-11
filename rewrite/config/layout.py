import os, sys

from utils import logger as ScoreboardLogger
from utils.font import FontCache
from utils import deep_update, read_json


class Layout:
    LAYOUT_DIRECTORY = os.path.abspath(os.path.join("../../coordinates"))
    FONTNAME_DEFAULT = "4x6"

    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.font_cache = FontCache(self.FONTNAME_DEFAULT)

        self._json = self.__fetch_layout()

    def font(self, font_name):
        """
        Fetches a font from the font cache.
        """
        return self.font_cache.fetch_font(font_name)

    def font_size(self, font_name):
        return self.font_cache.font_size(font_name)

    @property
    def default_font(self):
        return self.font_cache.default_font

    def __fetch_layout(self):
        filename = "coordinates/w{}h{}.json".format(self.width, self.height)
        reference_filename = "{}.example".format(filename)
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
