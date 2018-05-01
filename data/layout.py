from rgbmatrix import graphics
from utils import get_file
import json
import debug

FONTNAME_DEFAULT = "4x6"
FONTNAME_KEY = "font_name"

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

    self.font_cache = {}
    default_font = self.__load_font("4x6")
    self.font_cache = {"4x6": default_font}

  # Returns a dictionary with "font" and "size"
  def font(self, keypath):
    d = self.coords(keypath)
    try:
      return self.__get_font_object(d[FONTNAME_KEY])
    except KeyboardInterrupt as e:
      raise e
    except:
      return self.__get_font_object(FONTNAME_DEFAULT)
    
  def coords(self, keypath):
    try:
      d = self.__find_at_keypath(keypath)
    except KeyError as e:
      raise e

    if self.state in AVAILABLE_OPTIONAL_KEYS:
      if self.state in d:
        return d[self.state]
    return d

  def set_state(self, new_state=None):
    if new_state in AVAILABLE_OPTIONAL_KEYS:
      self.state = new_state
    else:
      self.state = None
      debug.log("Could not set state to requested {}".format(new_state))

  def __find_at_keypath(self, keypath):
    keys = keypath.split('.')
    rv = self.json
    for key in keys:
      rv = rv[key]
    return rv

  def __load_font(self, font_name):
    if font_name in self.font_cache:
      return self.font_cache[font_name]

    font = graphics.Font()
    font.LoadFont(get_file("Assets/{}.bdf".format(font_name)))
    return font

  def __parse_font_size(self, font_name):
    dimensions = font_name.split("x")
    return {"width": int(dimensions[0]), "height": int(dimensions[1])}

  def __get_font_object(self, font_name):
    f = self.__load_font(font_name)
    s = self.__parse_font_size(font_name)
    return {"font": f, "size": s}
