from data.bases import Bases
from data.inning import Inning
from data.outs import Outs
from data.pitches import Pitches
from data.team import Team
from data.atbat import AtBat


class Scoreboard:
    """Contains data for a current game.
    The data contains runs scored for both teams, and details about the current at-bat,
    including runners on base, balls, strikes, and outs.
    """

    def __init__(self, game_data):
        self.away_team = Team(
            game_data["gameData"]["teams"]["away"]["abbreviation"],
            game_data["liveData"]["linescore"]["teams"]["away"]["runs"],
            game_data["gameData"]["teams"]["away"]["teamName"],
        )
        self.home_team = Team(
            game_data["gameData"]["teams"]["home"]["abbreviation"],
            game_data["liveData"]["linescore"]["teams"]["home"]["runs"],
            game_data["gameData"]["teams"]["home"]["teamName"],
        )
        self.inning = Inning(game_data)
        self.bases = Bases(game_data)
        self.pitches = Pitches(game_data)
        self.outs = Outs(game_data)
        self.game_status = game_data["gameData"]["status"]["detailedState"]
        self.atbat = AtBat(game_data)
        self.batter = self.atbat.batter
        self.pitcher = self.atbat.pitcher

        try:
            self.note = game_data["liveData"]["linescore"]["note"]
        except:
            self.note = None

        try:
            self.reason = None  # TODO overview.reason
        except:
            self.reason = None

    def get_text_for_reason(self):
        if self.note:
            return self.note

        if self.reason:
            return self.reason

        return None

    def __str__(self):
        s = "<{} {}> {} ({}) @ {} ({}); Status: {}; Inning: (Number: {}; State: {}); B:{} S:{} O:{}; P:{}; AB:{}; Bases: {};".format(
            self.__class__.__name__,
            hex(id(self)),
            self.away_team.abbrev,
            str(self.away_team.runs),
            self.home_team.abbrev,
            str(self.home_team.runs),
            self.game_status,
            str(self.inning.number),
            str(self.inning.state),
            str(self.pitches.balls),
            str(self.pitches.strikes),
            str(self.outs.number),
            str(self.pitcher),
            str(self.batter),
            str(self.bases),
        )
        if self.reason:
            s += " Reason: '{}';".format(self.reason)
        if self.note:
            s += " Notes: '{}';".format(self.note)
        return s
