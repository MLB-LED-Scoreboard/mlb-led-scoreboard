from scoreboard import Scoreboard
from scoreboard_renderer import ScoreboardRenderer
from pprint import pprint
from rgbmatrix import RGBMatrix
import random
import sys
import time

def refresh_scoreboard(team):
  matrix = RGBMatrix()
  scoreboard = Scoreboard(team)
  renderer = ScoreboardRenderer(matrix, scoreboard)
  renderer.render_away_team()
  # TODO: Replace with LED matrix drawing
  pprint(scoreboard)

"""Refresh the scoreboard every 15 seconds. Default to Cubs if a team isn't given."""
team = sys.argv[1] if len(sys.argv) > 1 else 'Cubs'
starttime = time.time()
matrix = RGBMatrix()
while True:
  refresh_scoreboard(team)
  matrix.SetPixel(3, 3, random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
  time.sleep(15.0 - ((time.time() - starttime) % 15.0))
