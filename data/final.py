import mlbgame
import debug

UNKNOWN = 'Unknown'

class Final:
  def __init__(self, game):
    try:
      self.winning_team = game.w_team or UNKNOWN
    except:
      self.winning_team = UNKNOWN

    try:
      self.winning_pitcher = game.w_pitcher or UNKNOWN
    except:
      self.winning_pitcher = UNKNOWN

    try:
      self.winning_pitcher_wins = game.w_pitcher_wins or 0
    except:
      self.winning_pitcher_wins = 0

    try:
      self.winning_pitcher_losses = game.w_pitcher_losses or 0
    except:
      self.winning_pitcher_losses = 0

    try:
      self.losing_team = game.l_team or UNKNOWN
    except:
      self.losing_team = UNKNOWN

    try:
      self.losing_pitcher = game.l_pitcher or UNKNOWN
    except:
      self.losing_pitcher = UNKNOWN

    try:
      self.losing_pitcher_wins = game.l_pitcher_wins or 0
    except:
      self.losing_pitcher_wins = 0

    try:
      self.losing_pitcher_losses = game.l_pitcher_losses or 0
    except:
      self.losing_pitcher_losses = 0

  def __str__(self):
    s =  "<%s %s> " % (self.__class__.__name__, hex(id(self)))
    s += "W: %s %s-%s (%s), L: %s %s-%s (%s)" % (
      self.winning_pitcher, self.winning_pitcher_wins, self.winning_pitcher_losses, self.winning_team,
      self.losing_pitcher, self.losing_pitcher_wins, self.losing_pitcher_losses, self.losing_team)
    return s
