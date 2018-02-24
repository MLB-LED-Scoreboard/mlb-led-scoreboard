import mlbgame

class Pregame:
  def __init__(self, game):
    self.game = game
    self.game_data = self.__pregame_data()
  
  def __pregame_data(self):
    # The overview API is used to get the teams' abbreviations
    # as opposed to the full names
    game_data = {}

    try:
      overview = mlbgame.overview(self.game.game_id)
      game_data['away_team'] = overview.away_name_abbrev
      game_data['home_team'] = overview.home_name_abbrev
    except ValueError:
      # We can't find the overview page. Let's just abbreviate the teams manually
      game_data['away_team'] = self.game.away_team[:3]
      game_data['home_team'] = self.game.home_team[:3]
      game_data['error'] = "Game Data Not Found"

    game_data['time'] = self.game.game_start_time
    game_data['away_pitcher'] = self.game.p_pitcher_away or 'TBD'
    game_data['home_pitcher'] = self.game.p_pitcher_home or 'TBD'

    return game_data

  def __str__(self):
    s =  "<%s %s> " % (self.__class__.__name__, hex(id(self)))
    s += "%s @ %s, (%s), %s vs %s" % (
      self.game_data['away_team'], self.game_data['home_team'], self.game_data['time'], 
      self.game_data['away_pitcher'], self.game_data['home_pitcher'])

    if 'error' in self.game_data:
      s += ", Error: %s" % (self.game_data['error'])

    return s
