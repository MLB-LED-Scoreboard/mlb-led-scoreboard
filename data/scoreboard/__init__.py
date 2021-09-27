from data.game import Game
from data.scoreboard.atbat import AtBat
from data.scoreboard.bases import Bases
from data.scoreboard.inning import Inning
from data.scoreboard.outs import Outs
from data.scoreboard.pitches import Pitches
from data.scoreboard.team import Team


class Scoreboard:
    """Contains data for a current game.
    The data contains runs scored for both teams, and details about the current at-bat,
    including runners on base, balls, strikes, and outs.
    """

    def __init__(self, game: Game):
        self.away_team = Team(game.away_abbreviation(), game.away_score(), game.away_name())
        self.home_team = Team(game.home_abbreviation(), game.home_score(), game.home_name())
        self.inning = Inning(game)
        self.bases = Bases(game)
        self.pitches = Pitches(game)
        self.outs = Outs(game)
        self.game_status = game.status()
        self.atbat = AtBat(game)

        self.note = game.note()

        self.reason = game.reason()

        self.play_result = game.current_play_result()

    def homerun(self):
        return self.play_result == "home_run"

    def strikeout(self):
        return "strikeout" in self.play_result

    def strikeout_looking(self):
        return self.play_result == "strikeout_looking"

    def get_text_for_reason(self):
        if self.note:
            return self.note

        if self.reason:
            return self.reason

        return None

    def __str__(self):
        s = (
            "<{} {}> {} ({}) @ {} ({}); Status: {}; Inning: (Number: {};"
            " State: {}); B:{} S:{} O:{}; P:{}; AB:{}; Bases: {};".format(
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
                str(self.atbat.pitcher),
                str(self.atbat.batter),
                str(self.bases),
            )
        )
        if self.reason:
            s += " Reason: '{}';".format(self.reason)
        if self.note:
            s += " Notes: '{}';".format(self.note)
        return s
