from utils import get_file, deep_update
from layout import Layout
from color import Color
import json
import os
import sys
import debug

DEFAULT_ROTATE_RATE = 15.0
MINIMUM_ROTATE_RATE = 2.0
DEFAULT_ROTATE_RATES = {"live": DEFAULT_ROTATE_RATE, "final": DEFAULT_ROTATE_RATE, "pregame": DEFAULT_ROTATE_RATE}

class ScoreboardConfig:
  def __init__(self, filename, width, height):
    json = self.read_json(filename)
    self.preferred_team = json.get("preferred_team")
    self.preferred_division = json.get("preferred_division", "NL Central")
    self.rotate_games = json.get("rotate_games", False)
    self.rotate_rates = json.get("rotate_rates", DEFAULT_ROTATE_RATES)
    self.stay_on_live_preferred_team = json.get("stay_on_live_preferred_team", True)
    self.display_standings = json.get("display_standings", False)
    self.display_standings_on_offday = json.get("display_standings_on_offday", True)
    self.scroll_until_finished = json.get("scroll_until_finished", True)
    self.end_of_day = json.get("end_of_day", "00:00")
    self.display_full_team_names = json.get("display_full_team_names", True)
    self.slower_scrolling = json.get("slower_scrolling", False)
    self.debug_enabled = json.get("debug_enabled", False)

    # Get the layout info
    json = self.__get_layout(width, height)
    self.layout = Layout(json, width, height)

    # Store color information
    json = self.__get_colors("teams")
    self.team_colors = Color(json)
    json = self.__get_colors("scoreboard")
    self.scoreboard_colors = Color(json)

    #Check the rotate_rates to make sure it's valid and not silly
    self.check_rotate_rates()
    self.check_display_standings_on_offday()

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

  def check_display_standings_on_offday(self):
    if self.display_standings_on_offday == 2 and not self.preferred_team:
      print("Warning: You have requested standings to be displayed on a preferred team's offday but have no preferred team. Update \"preferred_team\" ")
      self.display_standings_on_offday = True
    elif self.display_standings_on_offday == 1:
      self.display_standings_on_offday = True
    elif self.display_standings_on_offday == 0:
      self.display_standings_on_offday = False

  def read_json(self, filename):
    j = {}
    path = get_file(filename)
    if os.path.isfile(path):
      j = json.load(open(path))
    return j

  def __get_colors(self, base_filename):
    filename = "ledcolors/{}.json".format(base_filename)
    reference_filename = "{}.example".format(filename)
    reference_colors = self.read_json(reference_filename)
    if not reference_colors:
      debug.error("Invalid {} reference color file. Make sure {} exists in ledcolors/".format(base_filename, base_filename))
      sys.exit(1)

    custom_colors = self.read_json(filename)
    if custom_colors:
      debug.log("Custom {} colors found. Merging with default reference colors.".format(base_filename))
      new_colors = deep_update(reference_colors, custom_colors)
      return new_colors
    return reference_colors

  def __get_layout(self, width, height):
    filename = "ledcoords/w{}h{}.json".format(width, height)
    reference_filename = "{}.example".format(filename)
    reference_layout = self.read_json(reference_filename)
    if not reference_layout:
      # Unsupported coordinates
      print("Invalid matrix dimensions provided. See top of README for supported dimensions.")
      print("If you would like to see new dimensions supported, please file an issue on GitHub!")
      sys.exit(1)

    # Load and merge any layout customizations
    custom_layout = self.read_json(filename)
    if custom_layout:
      debug.log("Custom {}x{} found. Merging with default reference layout.".format(width,height))
      new_layout = deep_update(reference_layout, custom_layout)
      return new_layout
    return reference_layout
