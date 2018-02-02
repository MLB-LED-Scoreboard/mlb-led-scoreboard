from rgbmatrix import RGBMatrix
from utils import args, refresh_scoreboard, bump_counter
import mlbgame
import time

args = args()

# TODO: Uncomment once the season starts, testing with random games for now
# games = mlbgame.games(year, month, day)[0]
games = mlbgame.games(2017, 5, 10)[0]

# Get the game to start on. If the provided team does not have a game today,
# or the team name isn't provided, then the first game in the list is used.
game_idx = 0
if args.team:
  game_idx = next(
      (i for i, game in enumerate(games) if game.away_team ==
      args.team or game.home_team == args.team), 0
  )
game = games[game_idx]

# Initialize the matrix and fill it in with a dark blue color
rgb = RGBMatrix()
matrix = rgb.CreateFrameCanvas()
matrix.Fill(7, 14, 25)

# Refresh the board every 15 seconds and rotate the games if the command flag is passed
starttime = time.time()
while True:
  success = refresh_scoreboard(matrix, game)
  matrix = rgb.SwapOnVSync(matrix)
  time.sleep(15.0 - ((time.time() - starttime) % 15.0))
  if args.rotate:
    game_idx = bump_counter(game_idx, games, bool(args.rotate))
    game = games[game_idx]
    matrix.Fill(7, 14, 25)

  if not success:
    # TODO https://github.com/ajbowler/mlb-led-scoreboard/issues/13
    continue
