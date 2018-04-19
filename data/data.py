from datetime import datetime, timedelta
import mlbgame
import debug

class Data:
  def __init__(self, config):
    # Save the parsed config
    self.config = config

    # Parse today's date and see if we should use today or yesterday
    self.year, self.month, self.day = self.__parse_today()

    # Flag to determine when to refresh data
    self.needs_refresh = True
    
    # Fetch the games for today
    self.refresh_games(self.year, self.month, self.day)

    # Fetch all standings data for today
    # (Good to have in case we add a standings screen while rotating scores)
    self.refresh_standings(self.date())

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

  def refresh_standings(self, date):
    try:
      self.standings = mlbgame.standings(date)
    except:
      debug.error("Failed to refresh standings for {}".format(date))

  def refresh_games(self, year, month, day):
    self.games = mlbgame.day(year, month, day)

  def refresh_overview(self):
    self.overview = mlbgame.overview(self.current_game().game_id)


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


