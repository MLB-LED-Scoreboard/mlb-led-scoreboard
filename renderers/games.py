from data.pregame import Pregame
from data.scoreboard import Scoreboard
from data.final import Final
from renderers.final import Final as FinalRenderer
from renderers.pregame import Pregame as PregameRenderer
from renderers.scoreboard import Scoreboard as ScoreboardRenderer
from renderers.status import Status as StatusRenderer
from utils import bump_counter, split_string
import renderers.error
import debug
import mlbgame
import ledcolors.scoreboard
import math
import time
import sys

# Times measured in seconds
FIFTEEN_SECONDS = 15.0
FIFTEEN_MINUTES = 900.0

# Refresh rates measured in seconds
SCROLL_TEXT_SLOW_RATE = 0.2
SCROLL_TEXT_FAST_RATE = 0.1

# Game statuses
SCHEDULED = 'Scheduled'
PRE_GAME = 'Pre-Game'
IN_PROGRESS = 'In Progress'
FINAL = 'Final'
GAME_OVER = 'Game Over' # Not sure what the difference is between this and final but it exists
POSTPONED = 'Postponed'
DELAYED = 'Delayed'
WARMUP = 'Warmup'

# If we run into a breaking error, pause for this amount of time before trying to continue
ERROR_WAIT = 10.0

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
    self.scroll_finished = False
    self.data_needs_refresh = True
    debug.log(self)

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

      try:
        if self.data_needs_refresh:
          overview = mlbgame.overview(game.game_id)
          self.data_needs_refresh = False

      # If a game_id can't be found, we fail gracefully and try the next game
      except ValueError as e:
        if str(e) == "Could not find a game with that id.":
          error_strings = ["Game ID","Not","Found"] + [game.game_id]
          self.__handle_error(e, error_strings)
          current_game_index = bump_counter(current_game_index, self.games)
          game = self.games[current_game_index]
        else:
          error_strings = split_string(str(e), self.canvas.width/4)
          self.__handle_error(e, error_strings)

        continue

      # Catch everything else. 
      except:
        err_type, error, traceback = sys.exc_info()
        error_strings = split_string(str(error), self.canvas.width/4)
        self.__handle_error(error, error_strings)
        continue

      self.__refresh_game(game, overview)

      if self.config.scroll_until_finished == False:
        self.scroll_finished = True

      refresh_rate = SCROLL_TEXT_FAST_RATE
      if self.config.slowdown_scrolling == True:
        refresh_rate = SCROLL_TEXT_SLOW_RATE
      if overview.status == IN_PROGRESS:
        refresh_rate = self.config.live_rotate_rate
        self.data_needs_refresh = True
        self.scroll_finished = True

      time.sleep(refresh_rate)

      endtime = time.time()
      if endtime - self.creation_time >= FIFTEEN_MINUTES:
        return
      time_delta = endtime - starttime

      self.canvas.Fill(*ledcolors.scoreboard.fill)

      rotate_rate = self.config.live_rotate_rate

      # Always use the default 15 seconds for our pregame rotations
      if overview.status == PRE_GAME or overview.status == SCHEDULED:
        rotate_rate = self.config.pregame_rotate_rate

      if overview.status == FINAL or overview.status == GAME_OVER:
        rotate_rate = self.config.final_rotate_rate

      if time_delta >= rotate_rate and self.scroll_finished:
        starttime = time.time()
        self.data_needs_refresh = True
        self.scroll_finished = False
        if self.config.rotate_games:
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

  def __refresh_game(self, game, overview):
    """Draws the provided game on the canvas."""
    if overview.status == PRE_GAME or overview.status == SCHEDULED or overview.status == WARMUP:
      pregame = Pregame(overview)
      renderer = PregameRenderer(self.canvas, pregame, self.current_scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())
    elif overview.status == GAME_OVER or overview.status == FINAL:
      final = Final(game)
      scoreboard = Scoreboard(overview)
      renderer = FinalRenderer(self.canvas, final, scoreboard, self.current_scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())
    elif overview.status == POSTPONED or overview.status == DELAYED:
      scoreboard = Scoreboard(overview)
      StatusRenderer(self.canvas, scoreboard).render()
    else:
      scoreboard = Scoreboard(overview)
      ScoreboardRenderer(self.canvas, scoreboard).render()
    self.canvas = self.matrix.SwapOnVSync(self.canvas)

  def __handle_error(self, error, error_strings):
    debug.error( "{} {}".format(str(error), error_strings) )
    renderers.error.render(self.matrix, self.canvas, error_strings)
    time.sleep(ERROR_WAIT)

  def __update_scrolling_text_pos(self, new_pos):
    """Updates the position of the probable starting pitcher text."""
    pos_after_scroll = self.current_scrolling_text_pos - 1
    if pos_after_scroll + new_pos < 0:
      self.scroll_finished = True
      self.current_scrolling_text_pos = self.canvas.width
    else:
      self.current_scrolling_text_pos = pos_after_scroll

  def __str__(self):
    s = "<%s %s> " % (self.__class__.__name__, hex(id(self)))
    s += "%s %s" % (self.current_scrolling_text_pos, time.strftime("%H:%M", time.localtime(self.creation_time)))
    return s
