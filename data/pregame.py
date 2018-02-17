import mlbgame

class Pregame:
  def __init__(self, game):
    self.game = game
    self.game_data = self.__pregame_data()
  
  def __pregame_data(self):
    # The overview API is used to get the teams' abbreviations
    # as opposed to the full names
    overview = mlbgame.overview(self.game.game_id)

    game_data = {}
    game_data['away_team'] = overview.away_name_abbrev
    game_data['home_team'] = overview.home_name_abbrev
    game_data['time'] = self.game.game_start_time
    game_data['away_pitcher'] = self.game.p_pitcher_away or 'TBD'
    game_data['home_pitcher'] = self.game.p_pitcher_home or 'TBD'
    return game_data
