from utils import get_file
import json
import os

class ScoreboardConfig:
  def __init__(self, filename):
    json = self.read_json(filename)
    self.preferred_team = json.get("preferred_team")
    self.preferred_division = json.get("preferred_division", "NL Central")
    self.rotate_games = json.get("rotate_games", False)
    self.display_standings = json.get("display_standings", False)
    self.debug_enabled = json.get("debug_enabled", False)

  def read_json(self, filename):
    j = {}
    path = get_file(filename)
    if os.path.isfile(path):
      j = json.load(open(path))
    return j
