from data.pregame import Pregame
from data.scoreboard import Scoreboard
from renderers.scoreboard import ScoreboardRenderer
from renderers.pregame import PregameRenderer
from utils import bump_counter
import mlbgame
import ledcolors.scoreboard
import math
import time

# Times measured in seconds
FIFTEEN_SECONDS = 15.0
FIFTEEN_MINUTES = 900.0

# Refresh rates measured in seconds
PREGAME_RATE = 0.2
SCOREBOARD_RATE = FIFTEEN_SECONDS

# Game statuses
PRE_GAME = 'Scheduled'
IN_PROGRESS = 'In Progress'
FINAL = 'Final'

class GameRenderer:
  """An object that loops through and renders a list of games.

  Properties:
    matrix                     - An instance of RGBMatrix
    canvas                     - The canvas associated with the matrix
    games                      - The list of games to render
    args                       - Any supplied command line arguments
    current_scrolling_text_pos - The current position of the probable starting
                                 pitcher text for pregames.
    creation_time              - The time at which this GameRender was created.
  """

  def __init__(self, matrix, canvas, games, config):
    """Initializes a GameRender
    """
    self.matrix = matrix
    self.canvas = canvas
    self.games = games
    self.config = config
    self.current_scrolling_text_pos = self.canvas.width
    self.creation_time = time.time()

  def render(self):
    """Renders a game or games depending on the configuration.
    Infinitely loops up to 15 minutes before a refresh of the list of games
    is required.
    """
    self.canvas.Fill(*ledcolors.scoreboard.fill)
    current_game_index = self.__get_game_from_args()
    game = self.games[current_game_index]
    starttime = time.time()

    while True:
      endtime = time.time()
      if endtime - self.creation_time >= FIFTEEN_MINUTES:
        return
      time_delta = endtime - starttime

      self.__refresh_game(game)
      refresh_rate = PREGAME_RATE if game.game_status == PRE_GAME else SCOREBOARD_RATE
      time.sleep(refresh_rate - ((time_delta) % refresh_rate))
      self.canvas.Fill(*ledcolors.scoreboard.fill)

      # TODO: https://github.com/ajbowler/mlb-led-scoreboard/issues/30
      # The time_delta comparison will need to change depending on scrolling text size
      if self.config.rotate_games and time_delta >= FIFTEEN_SECONDS:
        starttime = time.time()
        self.current_scrolling_text_pos = self.canvas.width
        current_game_index = bump_counter(current_game_index, self.games)
        game = self.games[current_game_index]

  def __get_game_from_args(self):
    """Returns the index of the game to render.
    If a preferred team was provided in the configuration that index is
    picked if it exists, otherwise the first game in the list is used.
    """
    game_idx = 0
    if self.config.preferred_team:
      game_idx = next(
          (i for i, game in enumerate(self.games) if game.away_team ==
           self.config.preferred_team or game.home_team == self.config.preferred_team), 0
      )
    return game_idx

  def __refresh_game(self, game):
    """Draws the provided game on the canvas."""
    game_overview = mlbgame.overview(game.game_id)
    if game_overview.status == PRE_GAME:
      pregame = Pregame(game)
      renderer = PregameRenderer(self.canvas, pregame, self.current_scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())
    else:
      scoreboard = Scoreboard(game)
      # TODO: https://github.com/ajbowler/mlb-led-scoreboard/issues/13
      # Render something else if a game's data is incomplete
      if not scoreboard.game_data:
        return
      ScoreboardRenderer(self.canvas, scoreboard).render()
    self.canvas = self.matrix.SwapOnVSync(self.canvas)

  def __update_scrolling_text_pos(self, new_pos):
    """Updates the position of the probable starting pitcher text."""
    pos_after_scroll = self.current_scrolling_text_pos - 1
    if pos_after_scroll + new_pos < 0:
      self.current_scrolling_text_pos = self.canvas.width
    else:
      self.current_scrolling_text_pos = pos_after_scroll
