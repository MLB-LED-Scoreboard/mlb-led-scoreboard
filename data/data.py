from datetime import datetime, timedelta
from final import Final
from pregame import Pregame
from scoreboard import Scoreboard
from status import Status
import layout
import mlbgame
import debug
import time

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

NETWORK_RETRY_SLEEP_TIME = 5.0

class Data:
  def __init__(self, config):
    # Save the parsed config
    self.config = config

    # Parse today's date and see if we should use today or yesterday
    self.year, self.month, self.day = self.__parse_today()

    # Flag to determine when to refresh data
    self.needs_refresh = True

    # Fetch the games for today
    self.refresh_games()

    # Fetch all standings data for today
    # (Good to have in case we add a standings screen while rotating scores)
    self.refresh_standings()

    # What game do we want to start on?
    self.current_game_index = self.game_index_for_preferred_team()


  #
  # Date

  def __parse_today(self):
    today = datetime.today()
    end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
    if end_of_day > datetime.now():
      today -= timedelta(days=1)
    return (today.year, today.month, today.day)

  def date(self):
    return datetime(self.year, self.month, self.day)


  #
  # mlbgame refresh

  def refresh_standings(self):
    try:
      self.standings = mlbgame.standings()
    except:
      debug.error("Failed to refresh standings.")

  def refresh_games(self):
    attempts_remaining = 5
    while attempts_remaining > 0:
      try:
        self.games = mlbgame.day(self.year, self.month, self.day)
        self.games_refresh_time = time.time()
        break
      except URLError, e:
        debug.error("URLError: {}".format(e.reason))
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)
      except ValueError:
        debug.error("ValueError: Failed to refresh list of games")
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)

  def refresh_overview(self):
    attempts_remaining = 5
    while attempts_remaining > 0:
      try:
        self.overview = mlbgame.overview(self.current_game().game_id)
        self.__update_layout_state()
        self.needs_refresh = False
        self.print_overview_debug()
        break
      except URLError, e:
        debug.error("URLError: {}".format(e.reason))
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)
      except ValueError:
        debug.error("ValueError: Failed to refresh overview for {}".format(self.current_game().game_id))
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)

    # If we run out of retries, just move on to the next game
    if attempts_remaining <= 0 and self.config.rotate_games:
      self.advance_to_next_game()

  def __update_layout_state(self):
    if self.overview.status == Status.WARMUP:
      self.config.layout.set_state(layout.LAYOUT_STATE_WARMUP)

    if self.overview.is_no_hitter == "Y":
      self.config.layout.set_state(layout.LAYOUT_STATE_NOHIT)

    if self.overview.is_perfect_game == "Y":
      self.config.layout.set_state(layout.LAYOUT_PERFECT_GAME)

  #
  # Standings

  def standings_for_preferred_division(self):
    return self.__standings_for(self.config.preferred_division)

  def __standings_for(self, division_name):
    return next(division for division in self.standings.divisions if division.name == division_name)


  #
  # Games

  def current_game(self):
    return self.games[self.current_game_index]

  def advance_to_next_game(self):
    self.current_game_index = self.__next_game_index()
    return self.current_game()

  def game_index_for_preferred_team(self):
    if self.config.preferred_team:
      return self.__game_index_for(self.config.preferred_team)
    else:
      return 0

  def __game_index_for(self, team_name):
    game_idx = 0
    game_idx = next((i for i, game in enumerate(self.games) if team_name in [game.away_team, game.home_team]), 0)
    return game_idx

  def __next_game_index(self):
    counter = self.current_game_index + 1
    if counter >= len(self.games):
      counter = 0
    return counter


  #
  # Offdays

  def is_offday_for_preferred_team(self):
    if self.config.preferred_team:
      return not (next((i for i, game in enumerate(self.games) if self.config.preferred_team in [game.away_team, game.home_team]), None))
    else:
      return True

  def is_offday(self):
    return not len(self.games)

  #
  # Debug info

  def print_overview_debug(self):
    debug.log("Overview Refreshed: {}".format(self.overview.id))
    debug.log("Pre: {}".format(Pregame(self.overview)))
    debug.log("Live: {}".format(Scoreboard(self.overview)))
    debug.log("Final: {}".format(Final(self.current_game())))

