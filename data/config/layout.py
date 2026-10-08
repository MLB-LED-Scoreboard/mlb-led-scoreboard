from data import status
from driver import graphics
from bullpen.logging import LOGGER

import os.path

FONTNAME_DEFAULT = "4x6"
FONTNAME_KEY = "font_name"

DIR_FONT_PATCHED = "assets/fonts/patched"
DIR_FONT_DRIVER = "submodules/matrix/fonts"

LAYOUT_STATE_WARMUP = "warmup"
LAYOUT_STATE_NOHIT = "nohit"
LAYOUT_STATE_PERFECT = "perfect_game"
AVAILABLE_OPTIONAL_KEYS = [FONTNAME_KEY, LAYOUT_STATE_WARMUP, LAYOUT_STATE_NOHIT, LAYOUT_STATE_PERFECT]


class Layout:
    def __init__(self, layout_json, width, height):
        self.json = layout_json
        self.width = width
        self.height = height
        self.state = None
        self.default_font_name = FONTNAME_DEFAULT
        self.default_font_name = self.coords("defaults.font_name")

        self.font_cache = {}

        # Cache the default font to start
        self.__get_font_object(self.default_font_name)

    def font(self, keypath):
        """
        Returns a dictionary with font properties. The font object resides under the "font" key.

        {
            "font": any,
            "path": str,
            "properties": {
                "width": int,
                "height": int
            }
        }
        """
        try:
            return self.__get_font_object(self.coords(keypath)[FONTNAME_KEY])
        except Exception:
            return self.__get_font_object(self.default_font_name)

    def coords(self, keypath):
        try:
            coord_dict = self.__find_at_keypath(keypath)
        except KeyError as e:
            raise e

        if not isinstance(coord_dict, dict) or not self.state in AVAILABLE_OPTIONAL_KEYS:
            return coord_dict

        if self.state in coord_dict:
            return coord_dict[self.state]

        return coord_dict

    def set_state(self, new_state=None):
        if new_state in AVAILABLE_OPTIONAL_KEYS:
            self.state = new_state
        else:
            self.state = None

    def state_for_game(self, game):
        new_state = None
        if game.status() == status.WARMUP:
            new_state = LAYOUT_STATE_WARMUP

        if game.is_no_hitter():
            new_state = LAYOUT_STATE_NOHIT

        if game.is_perfect_game():
            new_state = LAYOUT_STATE_PERFECT

        self.set_state(new_state)

    def state_is_warmup(self):
        return self.state == LAYOUT_STATE_WARMUP

    def state_is_nohitter(self):
        return self.state in [LAYOUT_STATE_NOHIT, LAYOUT_STATE_PERFECT]

    def __find_at_keypath(self, keypath):
        keys = keypath.split(".")
        rv = self.json
        for key in keys:
            rv = rv[key]
        return rv

    def __get_font_object(self, font_name):
        if font_name in self.font_cache:
            return self.font_cache[font_name]

        font_paths = [DIR_FONT_PATCHED, DIR_FONT_DRIVER]
        for font_path in font_paths:
            abs_path = os.path.abspath(os.path.join(__file__, "../../..", f"{font_path}/{font_name}.bdf"))

            if os.path.isfile(abs_path):
                font = graphics.Font()
                font.LoadFont(abs_path)

                self.font_cache[font_name] = {
                    "font": font,
                    "path": abs_path,
                } | self.__get_font_bdf_properties(abs_path)

                return self.font_cache[font_name]

    def __get_font_bdf_properties(self, path):
        size = { "width": 0, "height": 0 }
        found = False

        with open(path, 'r') as f:
            for _, line in enumerate(f):
                if not line.startswith("FONTBOUNDINGBOX"):
                    continue

                # https://xorg.freedesktop.org/docs/BDF/bdf.pdf
                # FONTBOUNDINGBOX W H Xoffset Yoffset
                _bbx, w, h, _xoffset, _yoffset = line.split(" ")

                size = { "width": int(w), "height": int(h) }
                found = True

                break

        if not found:
            LOGGER.warning(f"Unable to parse font bounding box for {path}")
        
        return { "size": size }

    def __eq__(self, other):

        return (
            isinstance(other, Layout)
            and self.json == other.json
            and self.width == other.width
            and self.height == other.height
        )

    def for_plugin(self, plugin_name: str) -> "Layout":

        plugins = self.json.get("plugins", {})
        if plugin_name in ("news", "standings"):
            # legacy workaround
            plugins = self.json

        plugin = plugins.get(plugin_name, {})
        json = {plugin_name: plugin}
        json["defaults"] = self.json["defaults"]
        plugin_layout = Layout(json, self.width, self.height)

        return plugin_layout
