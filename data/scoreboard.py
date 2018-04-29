from bases import Bases
from inning import Inning
from pitches import Pitches
from outs import Outs
from team import Team
import datetime
import debug

class Scoreboard:
  """Contains data for a current game.
  The data contains runs scored for both teams, and details about the current at-bat,
  including runners on base, balls, strikes, and outs.
  """

  def __init__(self, overview):
    self.away_team = Team(overview.away_name_abbrev, overview.away_team_runs, overview.away_team_name)
    self.home_team = Team(overview.home_name_abbrev, overview.home_team_runs, overview.home_team_name)
    self.inning = Inning(overview)
    self.bases = Bases(overview)
    self.pitches = Pitches(overview)
    self.outs = Outs(overview)
    self.game_status = overview.status

  def __str__(self):
    s = "<{} {}> {} ({}) @ {} ({}); Status: {}; Inning: (Number: {}; State: {}); B:{} S:{} O:{}; Bases: {}".format(
      self.__class__.__name__, hex(id(self)),
      self.away_team.abbrev, str(self.away_team.runs),
      self.home_team.abbrev, str(self.home_team.runs),
      self.game_status,
      str(self.inning.number),
      str(self.inning.state),
      str(self.pitches.balls),
      str(self.pitches.strikes),
      str(self.outs.number),
      str(self.bases))
    return s
