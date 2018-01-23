from scoreboard import Scoreboard
from pprint import pprint
import sys
import time

def refresh_scoreboard(team):
  scoreboard = Scoreboard(team)
  # TODO: Replace with LED matrix drawing
  pprint(scoreboard)

"""Refresh the scoreboard every 15 seconds. Default to Cubs if a team isn't given."""
team = sys.argv[1] if len(sys.argv) > 1 else 'Cubs'
starttime = time.time()
while True:
  refresh_scoreboard(team)
  time.sleep(15.0 - ((time.time() - starttime) % 15.0))
