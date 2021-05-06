from data.final import Final
from data.pregame import Pregame
from data.scoreboard import Scoreboard
from data.status import Status
from renderers.final import Final as FinalRenderer
from renderers.pregame import Pregame as PregameRenderer
from renderers.scoreboard import Scoreboard as ScoreboardRenderer
from renderers.status import StatusRenderer
from renderers.standings import StandingsRenderer
from renderers.offday import OffdayRenderer
from data.data import Data
import debug
import time

GAMES_REFRESH_RATE = 900.0
SCROLL_TEXT_FAST_RATE = 0.1
SCROLL_TEXT_SLOW_RATE = 0.2

class MainRenderer:
  def __init__(self, matrix, data):
    self.matrix = matrix
    self.data = data
    self.canvas = matrix.CreateFrameCanvas()
    self.scrolling_text_pos = self.canvas.width
    self.scrolling_status_pos = self.canvas.width
    self.scrolling_finished = False
    self.starttime = time.time()

  def render(self):
    self.starttime = time.time()

    # Always display the news ticker
    if self.data.config.news_ticker_always_display:
      self.__render_offday()

    # Always display the standings
    elif self.data.config.standings_always_display:
      self.__render_standings()

    # Full MLB Offday
    elif self.data.is_offday():
      if self.data.config.standings_mlb_offday:
        self.__render_standings()
      else:
        self.__render_offday()

    # Preferred Team Offday
    elif self.data.is_offday_for_preferred_team():
      if self.data.config.news_ticker_team_offday:
        self.__render_offday()
      elif self.data.config.standings_team_offday:
        self.__render_standings()
      else:
        self.__render_game()

    # Playball!
    else:
      self.__render_game()

  # Render an offday screen with the weather, clock and news
  def __render_offday(self):
    self.scrolling_finished = False

    while True:
      color = self.data.config.scoreboard_colors.color("default.background")
      self.canvas.Fill(color["r"], color["g"], color["b"])

      scroll_max_x = self.__max_scroll_x(self.data.config.layout.coords("offday.scrolling_text"))
      renderer = OffdayRenderer(self.canvas, self.data, self.scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())
      self.data.refresh_weather()
      self.data.refresh_news_ticker()
      self.canvas = self.matrix.SwapOnVSync(self.canvas)
      time.sleep(self.data.config.scrolling_speed)

  # Render the standings screen
  def __render_standings(self):
    try:
      StandingsRenderer(self.matrix, self.canvas, self.data).render()
    except Exception as ex:
      # Out of season off days don't always return standings so fall back on the offday renderer
      debug.error("Could not render standings.  Falling back to off day.")
      debug.error("{}: {}".format(type(ex).__name__, ex.args))
      self.__render_offday()

  # Renders a game screen based on it's status
  def __render_game(self):
    while True:
      # If we need to refresh the overview data, do that
      if self.data.needs_refresh:
        self.data.refresh_overview()

      # Draw the current game
      self.__draw_game(self.data.current_game(), self.data.overview)

      # Check if we need to scroll until it's finished
      if self.data.config.rotation_scroll_until_finished == False:
        self.scrolling_finished = True

      # Set the refresh rate
      refresh_rate = self.data.config.scrolling_speed

      # Currently the only thing that's always static is the live scoreboard
      if Status.is_static(self.data.overview.status):
        self.scrolling_finished = True

      # If the status is irregular and there's no 'reason' text, finish scrolling
      if Status.is_irregular(self.data.overview.status) and Scoreboard(self.data.overview).get_text_for_reason() is None:
        self.scrolling_finished = True

      time.sleep(refresh_rate)
      endtime = time.time()
      time_delta = endtime - self.starttime
      rotate_rate = self.__rotate_rate_for_status(self.data.overview.status)

      # If we're ready to rotate, let's do it
      if time_delta >= rotate_rate and self.scrolling_finished:
        self.starttime = time.time()
        self.scrolling_finished = False
        self.data.needs_refresh = True

        if Status.is_fresh(self.data.overview.status):
          self.scrolling_text_pos = self.canvas.width

        if self.__should_rotate_to_next_game(self.data.overview):
          self.scrolling_text_pos = self.canvas.width
          game = self.data.advance_to_next_game()

        if endtime - self.data.games_refresh_time >= GAMES_REFRESH_RATE:
          self.data.refresh_games()

        if self.data.needs_refresh:
          self.data.refresh_overview()

        if Status.is_complete(self.data.overview.status):
          if Final(self.data.current_game()).winning_pitcher == 'Unknown':
            self.data.refresh_games()

  def __rotate_rate_for_status(self, status):
    rotate_rate = self.data.config.rotation_rates_live
    if Status.is_pregame(status):
      rotate_rate = self.data.config.rotation_rates_pregame
    if Status.is_complete(status):
      rotate_rate = self.data.config.rotation_rates_final
    return rotate_rate

  def __should_rotate_to_next_game(self, overview):
    if self.data.config.rotation_enabled == False:
      return False

    stay_on_preferred_team = self.data.config.preferred_teams and not self.data.config.rotation_preferred_team_live_enabled
    if stay_on_preferred_team == False:
      return True

    showing_preferred_team = self.data.config.preferred_teams[0] in [overview.away_team_name, overview.home_team_name]
    if showing_preferred_team and Status.is_live(overview.status):
      if self.data.config.rotation_preferred_team_live_mid_inning == True and Status.is_inning_break(overview.inning_state):
        return True
      return False

    return True

  # Draws the provided game on the canvas
  def __draw_game(self, game, overview):
    color = self.data.config.scoreboard_colors.color("default.background")
    self.canvas.Fill(color["r"], color["g"], color["b"])

    # Draw the pregame renderer
    if Status.is_pregame(overview.status):
      scoreboard = Scoreboard(overview)
      scroll_max_x = self.__max_scroll_x(self.data.config.layout.coords("pregame.scrolling_text"))
      pregame = Pregame(overview, self.data.config.time_format)
      renderer = PregameRenderer(self.canvas, pregame, scoreboard, self.data, self.scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())

    # Draw the final game renderer
    elif Status.is_complete(overview.status):
      scroll_max_x = self.__max_scroll_x(self.data.config.layout.coords("final.scrolling_text"))
      final = Final(game)
      scoreboard = Scoreboard(overview)
      renderer = FinalRenderer(self.canvas, final, scoreboard, self.data, self.scrolling_text_pos)
      self.__update_scrolling_text_pos(renderer.render())

    # Draw the scoreboar renderer
    elif True: # Status.is_irregular(overview.status):
      scoreboard = Scoreboard(overview)
      if scoreboard.get_text_for_reason():
        scroll_max_x = self.__max_scroll_x(self.data.config.layout.coords("status.scrolling_text"))
        renderer = StatusRenderer(self.canvas, scoreboard, self.data, self.scrolling_text_pos, self.scrolling_status_pos)
        scrolling_text_pos, status_text_pos = renderer.render()

        self.__update_scrolling_status_pos(status_text_pos)
        self.__update_scrolling_text_pos(scrolling_text_pos)
      else:
        renderer = StatusRenderer(self.canvas, scoreboard, self.data, status_scroll_pos = self.scrolling_status_pos)
        _scrolling_text_pos, status_text_pos = renderer.render()

        self.__update_scrolling_status_pos(status_text_pos)
    else:
      scoreboard = Scoreboard(overview)
      ScoreboardRenderer(self.canvas, scoreboard, self.data).render()
    self.canvas = self.matrix.SwapOnVSync(self.canvas)

  def __max_scroll_x(self, scroll_coords):
    scroll_coords = self.data.config.layout.coords("final.scrolling_text")
    scroll_max_x = scroll_coords["x"] + scroll_coords["width"]
    if self.scrolling_text_pos > scroll_max_x:
      self.scrolling_text_pos = scroll_max_x
    return scroll_max_x

  def __update_scrolling_text_pos(self, new_pos):
    """Updates the position of the probable starting pitcher text."""
    pos_after_scroll = self.scrolling_text_pos - 1
    if pos_after_scroll + new_pos < 0:
      self.scrolling_finished = True
      self.scrolling_text_pos = self.canvas.width
    else:
      self.scrolling_text_pos = pos_after_scroll

  def __update_scrolling_status_pos(self, new_pos):
    """Updates the position of the status text."""
    pos_after_scroll = self.scrolling_status_pos - 1
    if pos_after_scroll + new_pos < 0:
      self.scrolling_status_pos = self.canvas.width
    else:
      self.scrolling_status_pos = pos_after_scroll
