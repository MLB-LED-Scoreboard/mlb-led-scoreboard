from data.final import Final
from data.pregame import Pregame
from data.scoreboard import Scoreboard
from data.status import Status
from renderers.final import Final as FinalRenderer
from renderers.pregame import Pregame as PregameRenderer
from renderers.scoreboard import Scoreboard as ScoreboardRenderer
from renderers.status import StatusRenderer
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
    scroll_finished            - Flag indicating whether any scrolling text has
                                 finished scrolling at least once.
    data_needs_refresh         - Flag indicating whether the data should be refreshed.
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
      if Status.is_static(overview.status):
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
      if Status.is_pregame(overview.status):
        rotate_rate = self.config.pregame_rotate_rate

      if Status.is_complete(overview.status):
        rotate_rate = self.config.final_rotate_rate

      if time_delta >= rotate_rate and self.scroll_finished:
        starttime = time.time()
        self.data_needs_refresh = True
        self.scroll_finished = False
        if Status.is_fresh(overview.status):
          self.current_scrolling_text_pos = self.canvas.width
        if self.__should_rotate_to_next_game(overview):
          self.current_scrolling_text_pos = self.canvas.width
          current_game_index = bump_counter(current_game_index, self.games)
          game = self.games[current_game_index]

  def __should_rotate_to_next_game(self, overview):
    if self.config.rotate_games == False:
      return False

    stay_on_preferred_team = self.config.preferred_team and self.config.stay_on_live_preferred_team
    if stay_on_preferred_team == False:
      return True

    showing_preferred_team = self.config.preferred_team in [overview.away_team_name, overview.home_team_name]
    if showing_preferred_team and Status.is_live(overview.status):
      return False

    return True

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
    if Status.is_pregame(overview.status):
      pregame = Pregame(overview)
      renderer = PregameRenderer(self.canvas, pregame, self.config.coords["pregame"], self.current_scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())
    elif Status.is_complete(overview.status):
      final = Final(game)
      scoreboard = Scoreboard(overview)
      renderer = FinalRenderer(self.canvas, final, scoreboard, self.config, self.current_scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())
    elif Status.is_irregular(overview.status):
      scoreboard = Scoreboard(overview)
      StatusRenderer(self.canvas, scoreboard, self.config).render()
    else:
      scoreboard = Scoreboard(overview)
      ScoreboardRenderer(self.canvas, scoreboard, self.config).render()
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
