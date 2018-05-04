from utils import get_file
import json
import debug
import os.path

class Color:
  def __init__(self, color_json):
    self.json = color_json

  def color(self, keypath):
    try:
      d = self.__find_at_keypath(keypath)
    except KeyError as e:
      raise e
    return d

  def __find_at_keypath(self, keypath):
    keys = keypath.split('.')
    rv = self.json
    for key in keys:
      rv = rv[key]
    return rv
