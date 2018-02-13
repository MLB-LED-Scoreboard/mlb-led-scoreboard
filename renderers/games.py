from data.scoreboard import Scoreboard
from renderers.scoreboard import Scoreboard as ScoreboardRenderer
from utils import bump_counter
import ledcolors.scoreboard
import time

FIFTEEN_MINUTES = 900

def render(matrix, canvas, games, args):
  # Get the game to start on. If the provided team does not have a game today,
  # or the team name isn't provided, then the first game in the list is used.
  game_idx = 0
  if args.team:
    game_idx = next(
        (i for i, game in enumerate(games) if game.away_team ==
         args.team or game.home_team == args.team), 0
    )
  game = games[game_idx]

  canvas.Fill(*ledcolors.scoreboard.fill)
  starttime = time.time()
  while True:
    endtime = time.time()
    delta = endtime - starttime
    if delta >= FIFTEEN_MINUTES:
      return

    success = __refresh_scoreboard(canvas, game)
    canvas = matrix.SwapOnVSync(canvas)
    
    # Refresh the board every 15 seconds and rotate the games
    # if the command flag is passed
    time.sleep(15.0 - ((delta) % 15.0))
    canvas.Fill(*ledcolors.scoreboard.fill)

    if args.rotate:
      game_idx = bump_counter(game_idx, games)
      game = games[game_idx]

def __refresh_scoreboard(canvas, game):
  renderer = {}
  if game.game_status == 'PRE_GAME':
    # pregame = Pregame(game)
    # renderer = PregameRenderer(canvas, pregame)
    # TODO
    pass
  else:
    scoreboard = Scoreboard(game)
    if not scoreboard.game_data:
      return False
    renderer = ScoreboardRenderer(canvas, scoreboard)
  renderer.render()
  return True
