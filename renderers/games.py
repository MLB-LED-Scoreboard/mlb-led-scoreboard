from data.pregame import Pregame
from data.scoreboard import Scoreboard
from renderers.scoreboard import Scoreboard as ScoreboardRenderer
from renderers.pregame import Pregame as PregameRenderer
from utils import bump_counter
import ledcolors.scoreboard
import math
import time

FIFTEEN_SECONDS = 15
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
  scrolling_text_pos = canvas.width
  starttime = original_start_time = time.time()

  while True:
    endtime = time.time()
    delta = endtime - starttime
    full_delta = endtime - original_start_time
    if full_delta >= FIFTEEN_MINUTES:
      return
    
    refresh_rate = 0.2 if game.game_status == 'PRE_GAME' else 15.0

    new_scrolling_text_pos = __refresh_scoreboard(canvas, game, scrolling_text_pos)
    if new_scrolling_text_pos is not None:
      scrolling_text_pos = new_scrolling_text_pos

    canvas = matrix.SwapOnVSync(canvas)
    
    # Refresh the board every 15 seconds and rotate the games
    # if the command flag is passed
    time.sleep(refresh_rate - ((delta) % refresh_rate))
    canvas.Fill(*ledcolors.scoreboard.fill)

    if args.rotate and delta >= FIFTEEN_SECONDS:
      starttime = time.time()
      scrolling_text_pos = canvas.width
      game_idx = bump_counter(game_idx, games)
      game = games[game_idx]

def __refresh_scoreboard(canvas, game, scrolling_text_pos):
  renderer = {}
  if game.game_status == 'PRE_GAME':
    pregame = Pregame(game)
    renderer = PregameRenderer(canvas, pregame, scrolling_text_pos)

    current_scrolling_text_pos = renderer.render()

    scrolling_text_pos -= 1
    if scrolling_text_pos + current_scrolling_text_pos < 0:
      scrolling_text_pos = canvas.width
    return scrolling_text_pos
  else:
    scoreboard = Scoreboard(game)
    if not scoreboard.game_data:
      return
    renderer = ScoreboardRenderer(canvas, scoreboard)
    renderer.render()
