import mlbgame
import datetime

class Scoreboard:
  """Contains data for a current game.
  The data contains runs scored for both teams, and details about the current at-bat,
  including runners on base, balls, strikes, and outs.
  """
  def __init__(self, team):
    """ Constructs a new Scoreboard and fetches data from MLB.
    
    team - The team to get today's game for.
    """
    self.team = team;
    self.game_data = self.__game_data(team)

  def __game_data(self, team):
    now = datetime.datetime.now()
    day = now.day
    month = now.month
    year = now.year

    # TODO: Uncomment once the season starts
    # For now, let's re-live one of the Cubs' world series wins
    # 
    # games = mlbgame.games(year, month, day, home=team, away=team)
    games = mlbgame.games(2016, 11, 1, home=team, away=team)
    return self.__current_game_data(games[0][0]) if len(games) else False

  def __current_game_data(self, game):
    game_id = game.game_id

    overview = mlbgame.overview(game_id)
    game_data = {}
    game_data['away_team'] = overview.away_name_abbrev
    game_data['home_team'] = overview.home_name_abbrev
    game_data['inning'] = self.__current_inning(game_id)

    from pprint import pprint
    pprint(game_data)
    return game_data

  def __current_inning(self, game_id):
    innings = mlbgame.game_events(game_id)

    inning_status = {}
    inning_status['number'] = len(innings)

    current_inning = innings[-1]
    is_bottom = bool(len(current_inning.bottom))
    at_bats = current_inning.bottom if is_bottom else current_inning.top

    inning_status['bottom'] = is_bottom
    inning_status['at_bat'] = self.__current_at_bat(at_bats[-1])
    return inning_status

  def __current_at_bat(self, current_at_bat):
    at_bat = {}
    at_bat['away_team_runs'] = current_at_bat.away_team_runs
    at_bat['home_team_runs'] = current_at_bat.home_team_runs
    at_bat['outs'] = current_at_bat.o
    at_bat['balls'] = current_at_bat.b
    at_bat['strikes'] = current_at_bat.s
    at_bat['bases'] = self.__runners_on_base(current_at_bat)
    return at_bat

  def __runners_on_base(self, at_bat):
    runners = []
    runners.append(bool(at_bat.b1))
    runners.append(bool(at_bat.b2))
    runners.append(bool(at_bat.b3))
    return runners
