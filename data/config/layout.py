from driver import graphics

import os.path

import bdfparser

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
        '''
        Returns a dictionary with font properties. The font object resides under the "font" key.

        {
            "font": any,
            "path": str,
            "bdf_headers": dict[str, any],
            "properties": {
                "width": int,
                "height": int
            }
        }
        '''
        d = self.coords(keypath)
        try:
            return self.__get_font_object(d[FONTNAME_KEY])
        except KeyboardInterrupt as e:
            raise e
        except:
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
            abs_path = os.path.abspath(
                os.path.join(
                    __file__, "../../..", f"{font_path}/{font_name}.bdf"
                )
            )

            if os.path.isfile(abs_path):
                font = graphics.Font()
                font.LoadFont(abs_path)

                self.font_cache[font_name] = {
                    "font": font,
                    "path": abs_path,
                } | self.__get_font_bdf_properties(abs_path)

                return self.font_cache[font_name]
            
    def __get_font_bdf_properties(self, path):
        bdf = bdfparser.Font(path)

        return {
            "bdf_headers": bdf.headers,
            "size": {
                "width": bdf.headers["fbbx"],
                "height": bdf.headers["fbby"]
            }
        }
