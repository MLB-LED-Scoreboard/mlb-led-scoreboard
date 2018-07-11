from utils import get_file, deep_update
from layout import Layout
from color import Color
import json
import os
import sys
import debug

SCROLLING_SPEEDS = [0.3, 0.2, 0.1, 0.05]
DEFAULT_ROTATE_RATE = 15.0
MINIMUM_ROTATE_RATE = 2.0
DEFAULT_ROTATE_RATES = {"live": DEFAULT_ROTATE_RATE, "final": DEFAULT_ROTATE_RATE, "pregame": DEFAULT_ROTATE_RATE}

class ScoreboardConfig:
  def __init__(self, filename_base, width, height):
    json = self.__get_config(filename_base)

    # Preferred Teams/Divisions
    self.preferred_teams = json["preferred"]["teams"]
    self.preferred_divisions = json["preferred"]["divisions"]

    # Display Standings
    self.standings_team_offday = json["standings"]["team_offday"]
    self.standings_mlb_offday = json["standings"]["mlb_offday"]
    self.standings_always_display = json["standings"]["always_display"]
    self.standings_display_offday = False

    # Rotation
    self.rotation_enabled = json["rotation"]["enabled"]
    self.rotation_scroll_until_finished = json["rotation"]["scroll_until_finished"]
    self.rotation_rates = json["rotation"]["rates"]
    self.rotation_preferred_team_live_enabled = json["rotation"]["while_preferred_team_live"]["enabled"]

    # Misc config options
    self.end_of_day = json["end_of_day"]
    self.full_team_names = json["full_team_names"]
    self.scrolling_speed = SCROLLING_SPEEDS[json["scrolling_speed"]]
    self.debug = json["debug"]

    # Get the layout info
    json = self.__get_layout(width, height)
    self.layout = Layout(json, width, height)

    # Store color information
    json = self.__get_colors("teams")
    self.team_colors = Color(json)
    json = self.__get_colors("scoreboard")
    self.scoreboard_colors = Color(json)

    #Check the rotation_rates to make sure it's valid and not silly
    self.check_rotate_rates()

  def check_rotate_rates(self):
    if isinstance(self.rotation_rates, dict) == False:
      try:
        rate = float(self.rotation_rates)
        self.rotation_rates = {"live": rate, "final": rate, "pregame": rate}
      except:
        debug.warning("rotation_rates should be a Dict or Float. Using default value. {}".format(DEFAULT_ROTATE_RATES))
        self.rotation_rates = DEFAULT_ROTATE_RATES

    for key, value in list(self.rotation_rates.items()):
      try:
        # Try and cast whatever the user passed into a float
        rate = float(value)
        self.rotation_rates[key] = rate
      except:
        # Use the default rotate rate if it fails
        debug.warning("Unable to convert rotate_rates[\"{}\"] to a Float. Using default value. ({})".format(key, DEFAULT_ROTATE_RATE))
        self.rotation_rates[key] = DEFAULT_ROTATE_RATE

      if self.rotation_rates[key] < MINIMUM_ROTATE_RATE:
        debug.warning("rotate_rates[\"{}\"] is too low. Please set it greater than {}. Using default value. ({})".format(key, MINIMUM_ROTATE_RATE, DEFAULT_ROTATE_RATE))
        self.rotation_rates[key] = DEFAULT_ROTATE_RATE

    # Setup some nice attributes to make sure they all exist
    self.rotation_rates_live = self.rotation_rates.get("live", DEFAULT_ROTATE_RATES["live"])
    self.rotation_rates_final = self.rotation_rates.get("final", DEFAULT_ROTATE_RATES["final"])
    self.rotation_rates_pregame = self.rotation_rates.get("pregame", DEFAULT_ROTATE_RATES["pregame"])

  def read_json(self, filename):
    j = {}
    path = get_file(filename)
    if os.path.isfile(path):
      j = json.load(open(path))
    return j

  def __get_config(self, base_filename):
    filename = "{}.json".format(base_filename)
    reference_filename = "{}.example".format(filename)
    reference_config = self.read_json(reference_filename)
    if not reference_filename:
      debug.error("Invalid {} reference config file. Make sure {} exists.".format(base_filename, base_filename))
      sys.exit(1)

    custom_config = self.read_json(filename)
    if custom_config:
      new_config = deep_update(reference_config, custom_config)
      return new_config
    return reference_config

  def __get_colors(self, base_filename):
    filename = "ledcolors/{}.json".format(base_filename)
    reference_filename = "{}.example".format(filename)
    reference_colors = self.read_json(reference_filename)
    if not reference_colors:
      debug.error("Invalid {} reference color file. Make sure {} exists in ledcolors/".format(base_filename, base_filename))
      sys.exit(1)

    custom_colors = self.read_json(filename)
    if custom_colors:
      debug.info("Custom '{}.json' colors found. Merging with default reference colors.".format(base_filename))
      new_colors = deep_update(reference_colors, custom_colors)
      return new_colors
    return reference_colors

  def __get_layout(self, width, height):
    filename = "ledcoords/w{}h{}.json".format(width, height)
    reference_filename = "{}.example".format(filename)
    reference_layout = self.read_json(reference_filename)
    if not reference_layout:
      # Unsupported coordinates
      debug.error("Invalid matrix dimensions provided. See top of README for supported dimensions.\nIf you would like to see new dimensions supported, please file an issue on GitHub!")
      sys.exit(1)

    # Load and merge any layout customizations
    custom_layout = self.read_json(filename)
    if custom_layout:
      debug.info("Custom '{}x{}.json' found. Merging with default reference layout.".format(width,height))
      new_layout = deep_update(reference_layout, custom_layout)
      return new_layout
    return reference_layout
