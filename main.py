from scoreboard import Scoreboard
from scoreboard_renderer import ScoreboardRenderer
from pprint import pprint
from rgbmatrix import RGBMatrix
import random
import sys
import time

def refresh_scoreboard(matrix, team):
  scoreboard = Scoreboard(team)
  renderer = ScoreboardRenderer(matrix, scoreboard)
  renderer.render_team_colors()
  renderer.render_team_text()
  renderer.render_pitches()
  renderer.render_outs()
  pprint(scoreboard)

"""Refresh the scoreboard every 15 seconds. Default to Cubs if a team isn't given."""
team = sys.argv[1] if len(sys.argv) > 1 else 'Cubs'
starttime = time.time()
matrix = RGBMatrix()
matrix.Fill(7, 14, 25)

while True:
  refresh_scoreboard(matrix, team)
  time.sleep(15.0 - ((time.time() - starttime) % 15.0))
