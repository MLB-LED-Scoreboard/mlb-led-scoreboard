from utils import get_file
import json
import os

DEFAULT_ROTATE_RATE = 15.0
MINIMUM_ROTATE_RATE = 2.0

class ScoreboardConfig:
  def __init__(self, filename):
    json = self.read_json(filename)
    self.preferred_team = json.get("preferred_team")
    self.preferred_division = json.get("preferred_division", "NL Central")
    self.rotate_games = json.get("rotate_games", False)
    self.rotate_rate = json.get("rotate_rate", DEFAULT_ROTATE_RATE)
    self.display_standings = json.get("display_standings", False)
    self.scroll_until_finished = json.get("scroll_until_finished", True)
    self.slowdown_scrolling = json.get("slowdown_scrolling", False)
    self.debug_enabled = json.get("debug_enabled", False)

    #Check the rotate_rate to make sure it's valid and not silly
    self.check_rotate_rate()

  def check_rotate_rate(self):
    try:
      # Try and cast whatever the user passed into a float
      self.rotate_rate = float(self.rotate_rate)
    except:
      print "Warning: Unable to convert rotate_rate to a Float. Using default value. ({})".format(DEFAULT_ROTATE_RATE)
      self.rotate_rate = DEFAULT_ROTATE_RATE

    if self.rotate_rate < MINIMUM_ROTATE_RATE:
      print "Warning: rotate_rate is too low. Please set it greater than {}. Using default value. ({})".format(MINIMUM_ROTATE_RATE, DEFAULT_ROTATE_RATE)
      self.rotate_rate = DEFAULT_ROTATE_RATE

  def read_json(self, filename):
    j = {}
    path = get_file(filename)
    if os.path.isfile(path):
      j = json.load(open(path))
    return j
