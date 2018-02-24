import mlbgame
import datetime

class Scoreboard:
  """Contains data for a current game.
  The data contains runs scored for both teams, and details about the current at-bat,
  including runners on base, balls, strikes, and outs.
  """
  def __init__(self, game):
    """ Constructs a new Scoreboard and fetches data from MLB.

    game - The game to display.
    """
    self.game = game
    self.game_data = self.__current_game_data(game)

  def __current_game_data(self, game):
    game_id = game.game_id

    overview = mlbgame.overview(game_id)
    game_data = {}
    game_data['away_team'] = overview.away_name_abbrev
    game_data['home_team'] = overview.home_name_abbrev
    try:
      game_data['inning'] = self.__current_inning(overview)
    except ValueError:
      print('No game data could be found for %s @ %s' % (game_data['away_team'], game_data['home_team']))
      return False
    return game_data

  def __current_inning(self, game_overview):
    inning_status = {}
    inning_status['number'] = game_overview.inning

    # TODO: inning_state returns 'Bottom', 'Top', 'End', 'Middle'
    inning_status['bottom'] = game_overview.inning_state == 'Bottom'
    inning_status['status'] = game_overview.inning_state
    inning_status['at_bat'] = self.__current_at_bat(game_overview)
    return inning_status

  def __current_at_bat(self, game_overview):
    at_bat = {}
    at_bat['away_team_runs'] = game_overview.away_team_runs
    at_bat['home_team_runs'] = game_overview.home_team_runs
    at_bat['outs'] = game_overview.outs
    at_bat['balls'] = game_overview.balls
    at_bat['strikes'] = game_overview.strikes
    at_bat['bases'] = self.__runners_on_base(game_overview)
    return at_bat

  def __runners_on_base(self, game_overview):
    if game_overview.runner_on_base_status == 0:
      return [False,False,False]

    runners = []
    runners.append(self.__runner_on_base(game_overview, '1b'))
    runners.append(self.__runner_on_base(game_overview, '2b'))
    runners.append(self.__runner_on_base(game_overview, '3b'))
    return runners

  def __runner_on_base(self, game_overview, base):
    try:
      getattr(game_overview, 'runner_on_' + base)
      return True
    except AttributeError:
      return False
