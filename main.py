from scoreboard import Scoreboard
from scoreboard_renderer import ScoreboardRenderer
from rgbmatrix import RGBMatrix
import mlbgame
import random
import sys
import time


def refresh_scoreboard(matrix, game):
  scoreboard = Scoreboard(game)
  if not scoreboard.game_data:
    return False
  renderer = ScoreboardRenderer(matrix, scoreboard)
  renderer.render()
  return True

def bump_counter(counter, arr, rotate):
  counter += 1
  if counter >= len(arr) and rotate:
    counter = 0
  return counter

default_team = sys.argv[1] if len(sys.argv) > 1 else 'Cubs'
# TODO: Uncomment once the season starts, testing with random games for now
# games = mlbgame.games(year, month, day)[0]
games = mlbgame.games(2017, 5, 10)[0]

# Get the game to start on. If the provided team does not have a game today
# then the first game in the list is used.
game_idx = next(
    (i for i, game in enumerate(games) if game.away_team ==
     default_team or game.home_team == default_team), 0
)
game = games[game_idx]

# Initialize the matrix and fill it in with a dark blue color
matrix = RGBMatrix()
matrix.Fill(7, 14, 25)

rotate_games = len(sys.argv) >= 3 and (
    sys.argv[2] == '--rotate' or sys.argv[2] == '-r')

# Refresh the board every 15 seconds and rotate the games if the command flag is passed
starttime = time.time()
while True:
  success = refresh_scoreboard(matrix, game)
  game_idx = bump_counter(game_idx, games, rotate_games)
  game = games[game_idx]
  time.sleep(15.0 - ((time.time() - starttime) % 15.0))
  
  matrix.Fill(7, 14, 25)
  if not success:
    # TODO https://github.com/ajbowler/mlb-led-scoreboard/issues/13
    continue
