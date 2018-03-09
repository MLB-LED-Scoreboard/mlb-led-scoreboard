from utils import get_file
import json
import os

DEFAULT_ROTATE_RATE = 15.0
MINIMUM_ROTATE_RATE = 2.0
DEFAULT_ROTATE_RATES = {"live": DEFAULT_ROTATE_RATE, "final": DEFAULT_ROTATE_RATE, "pregame": DEFAULT_ROTATE_RATE}

class ScoreboardConfig:
  def __init__(self, filename):
    json = self.read_json(filename)
    self.preferred_team = json.get("preferred_team")
    self.preferred_division = json.get("preferred_division", "NL Central")
    self.rotate_games = json.get("rotate_games", False)
    self.rotate_rates = json.get("rotate_rates", DEFAULT_ROTATE_RATES)
    self.stay_on_live_preferred_team = json.get("stay_on_live_preferred_team", True)
    self.display_standings = json.get("display_standings", False)
    self.scroll_until_finished = json.get("scroll_until_finished", True)
    self.slowdown_scrolling = json.get("slowdown_scrolling", False)
    self.debug_enabled = json.get("debug_enabled", False)

    #Check the rotate_rates to make sure it's valid and not silly
    self.check_rotate_rates()

  def check_rotate_rates(self):
    if isinstance(self.rotate_rates, dict) == False:
      try:
        rate = float(self.rotate_rates)
        self.rotate_rates = {"live": rate, "final": rate, "pregame": rate}
      except:
        print "Warning: rotate_rates should be a Dict or Float. Using default value. {}".format(DEFAULT_ROTATE_RATES)
        self.rotate_rates = DEFAULT_ROTATE_RATES

    for key, value in list(self.rotate_rates.items()):
      try:
        # Try and cast whatever the user passed into a float
        rate = float(value)
        self.rotate_rates[key] = rate
      except:
        # Use the default rotate rate if it fails
        print "Warning: Unable to convert rotate_rates[\"{}\"] to a Float. Using default value. ({})".format(key, DEFAULT_ROTATE_RATE)
        self.rotate_rates[key] = DEFAULT_ROTATE_RATE

      if self.rotate_rates[key] < MINIMUM_ROTATE_RATE:
        print "Warning: rotate_rates[\"{}\"] is too low. Please set it greater than {}. Using default value. ({})".format(key, MINIMUM_ROTATE_RATE, DEFAULT_ROTATE_RATE)
        self.rotate_rates[key] = DEFAULT_ROTATE_RATE

    # Setup some nice attributes to make sure they all exist
    self.live_rotate_rate = self.rotate_rates.get("live", DEFAULT_ROTATE_RATES["live"])
    self.final_rotate_rate = self.rotate_rates.get("final", DEFAULT_ROTATE_RATES["final"])
    self.pregame_rotate_rate = self.rotate_rates.get("pregame", DEFAULT_ROTATE_RATES["pregame"])

  def read_json(self, filename):
    j = {}
    path = get_file(filename)
    if os.path.isfile(path):
      j = json.load(open(path))
    return j
