from datetime import datetime, timedelta
from final import Final
from pregame import Pregame
from scoreboard import Scoreboard
from status import Status
from inning import Inning
from weather import Weather
from headlines import Headlines
import urllib
import layout
import mlbgame
import debug
import time

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError

NETWORK_RETRY_SLEEP_TIME = 10.0

class Data:
  def __init__(self, config):
    # Save the parsed config
    self.config = config

    # Parse today's date and see if we should use today or yesterday
    self.set_current_date()

    # Flag to determine when to refresh data
    self.needs_refresh = True

    # Fetch the games for today
    self.refresh_games()

    # Fetch all standings data for today
    # (Good to have in case we add a standings screen while rotating scores)
    self.refresh_standings()

    # What game do we want to start on?
    self.current_game_index = self.game_index_for_preferred_team()
    self.current_division_index = 0

    # Network status state
    self.network_issues = False

    # Weather info
    self.weather = Weather(self.config.weather_apikey, self.config.weather_location, self.config.weather_metric_units)

    # News headlines
    self.headlines = Headlines(self.config)


  #
  # Date

  def __parse_today(self):
    if self.config.demo_date:
      today = datetime.strptime(self.config.demo_date, '%Y-%m-%d')
    else:
      today = datetime.today()
    end_of_day = datetime.strptime(self.config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
    if end_of_day > datetime.now():
      today -= timedelta(days=1)
    return (today.year, today.month, today.day)

  def date(self):
    return datetime(self.year, self.month, self.day)

  def set_current_date(self):
    self.year, self.month, self.day = self.__parse_today()


  #
  # mlbgame refresh

  def refresh_standings(self):
    try:
      self.standings = mlbgame.standings()
    except:
      debug.error("Failed to refresh standings.")

  def refresh_games(self):
    debug.log("Updating games for {}/{}/{}".format(self.month, self.day, self.year))
    urllib.urlcleanup()
    attempts_remaining = 5
    while attempts_remaining > 0:
      try:
        current_day = self.day
        self.set_current_date()

        all_games = mlbgame.day(self.year, self.month, self.day)
        if self.config.rotation_only_preferred:
          self.games = self.__filter_list_of_games(all_games, self.config.preferred_teams)
        else:
          self.games = all_games

        if current_day != self.day:
          self.current_game_index = self.game_index_for_preferred_team()
        self.games_refresh_time = time.time()
        self.network_issues = False
        break
      except URLError, e:
        self.network_issues = True
        debug.error("Networking error while refreshing the master list of games. {} retries remaining.".format(attempts_remaining))
        debug.error("URLError: {}".format(e.reason))
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)
      except ValueError:
        self.network_issues = True
        debug.error("Value Error while refreshing master list of games. {} retries remaining.".format(attempts_remaining))
        debug.error("ValueError: Failed to refresh list of games")
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)

  def refresh_overview(self):
    urllib.urlcleanup()
    attempts_remaining = 5
    while attempts_remaining > 0:
      try:
        self.overview = mlbgame.overview(self.current_game().game_id)
        self.__update_layout_state()
        self.needs_refresh = False
        self.print_overview_debug()
        self.network_issues = False
        break
      except URLError, e:
        self.network_issues = True
        debug.error("Networking Error while refreshing the current overview. {} retries remaining.".format(attempts_remaining))
        debug.error("URLError: {}".format(e.reason))
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)
      except ValueError:
        self.network_issues = True
        debug.error("Value Error while refreshing current overview. {} retries remaining.".format(attempts_remaining))
        debug.error("ValueError: Failed to refresh overview for {}".format(self.current_game().game_id))
        attempts_remaining -= 1
        time.sleep(NETWORK_RETRY_SLEEP_TIME)

    # If we run out of retries, just move on to the next game
    if attempts_remaining <= 0 and self.config.rotation_enabled:
      self.advance_to_next_game()

  def refresh_weather(self):
    self.weather.update()

  def refresh_news_ticker(self):
    self.headlines.update()

  # Will use a network call to fetch the preferred team's game overview
  def fetch_preferred_team_overview(self):
    if not self.is_offday_for_preferred_team():
      urllib.urlcleanup()
      game = self.games[self.game_index_for_preferred_team()]
      game_overview = mlbgame.overview(game.game_id)
      debug.log("Preferred Team's Game Status: {}, {} {}".format(game_overview.status, game_overview.inning_state, game_overview.inning))
      return game_overview

  def __update_layout_state(self):
    self.config.layout.set_state()
    if self.overview.status == Status.WARMUP:
      self.config.layout.set_state(layout.LAYOUT_STATE_WARMUP)

    if self.overview.is_no_hitter == "Y":
      self.config.layout.set_state(layout.LAYOUT_STATE_NOHIT)

    if self.overview.is_perfect_game == "Y":
      self.config.layout.set_state(layout.LAYOUT_STATE_PERFECT)

  #
  # Standings

  def standings_for_preferred_division(self):
    return self.__standings_for(self.config.preferred_divisions[0])

  def __standings_for(self, division_name):
    return next(division for division in self.standings.divisions if division.name == division_name)

  def current_standings(self):
    return self.__standings_for(self.config.preferred_divisions[self.current_division_index])

  def advance_to_next_standings(self):
    self.current_division_index = self.__next_division_index()
    return self.current_standings()

  def __next_division_index(self):
    counter = self.current_division_index + 1
    if counter >= len(self.config.preferred_divisions):
      counter = 0
    return counter

  #
  # Games

  def current_game(self):
    return self.games[self.current_game_index]

  def advance_to_next_game(self):
    # We only need to check the preferred team's game status if we're
    # rotating during mid-innings
    if self.config.rotation_preferred_team_live_mid_inning and not self.is_offday_for_preferred_team():
      preferred_overview = self.fetch_preferred_team_overview()
      if Status.is_live(preferred_overview.status) and not Status.is_inning_break(preferred_overview.inning_state):
        self.current_game_index = self.game_index_for_preferred_team()
        self.overview = preferred_overview
        self.needs_refresh = False
        self.__update_layout_state()
        self.print_overview_debug()
        return self.current_game()
    self.current_game_index = self.__next_game_index()
    return self.current_game()

  def game_index_for_preferred_team(self):
    if self.config.preferred_teams:
      return self.__game_index_for(self.config.preferred_teams[0])
    else:
      return 0

  def __filter_list_of_games(self, games, teams):
    return list(game for game in set(games) if set([game.away_team, game.home_team]).intersection(set(teams)))

  def __game_index_for(self, team_name):
    team_index = 0
    team_idxs = [i for i, game in enumerate(self.games) if team_name in [game.away_team, game.home_team]]
    if len(team_idxs) > 0:
      attempts_remaining = 5
      while attempts_remaining > 0:
        try:
          team_index = next((i for i in team_idxs if Status.is_live(mlbgame.overview(self.games[i].game_id))), team_idxs[0])
          self.network_issues = False
          break
        except URLError, e:
          self.network_issues = True
          debug.error("Networking Error while refreshing live game status of {}. {} retries remaining.".format(team_name,attempts_remaining))
          debug.error("URLError: {}".format(e.reason))
          attempts_remaining -= 1
          time.sleep(NETWORK_RETRY_SLEEP_TIME)
        except ValueError:
          self.network_issues = True
          debug.error("Value Error while refreshing live game status of {}. {} retries remaining.".format(team_name,attempts_remaining))
          debug.error("ValueError: Failed to refresh overview for {}".format(self.current_game().game_id))
          attempts_remaining -= 1
          time.sleep(NETWORK_RETRY_SLEEP_TIME)

      if attempts_remaining <= 0:
        debug.error("Major networking error while refreshing live game status of {}".format(team_name))
        debug.error("Returning team_index of 0 because we ran out of networking retries.")

    return team_index

  def __next_game_index(self):
    counter = self.current_game_index + 1
    if counter >= len(self.games):
      counter = 0
    return counter

  #
  # Offdays

  def is_offday_for_preferred_team(self):
    if self.config.preferred_teams:
      return not any([self.config.preferred_teams[0] in [game.away_team, game.home_team] for game in self.games])
    else:
      return True

  def is_offday(self):
    return not len(self.games)

  #
  # Debug info

  def print_overview_debug(self):
    debug.log("Overview Refreshed: {}".format(self.overview.id))
    debug.log("Pre: {}".format(Pregame(self.overview, self.config.time_format)))
    debug.log("Live: {}".format(Scoreboard(self.overview)))
    debug.log("Final: {}".format(Final(self.current_game())))

