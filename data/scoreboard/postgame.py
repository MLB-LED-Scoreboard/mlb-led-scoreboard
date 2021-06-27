from data.game import Game

PITCHER_UNKNOWN = "Unknown"


class Postgame:
    def __init__(self, game: Game):

        winner_side = game.winning_team()

        winner = game.decision_pitcher_id("winner")
        if winner is not None:
            self.winning_pitcher = game.full_name(winner)
            self.winning_pitcher_wins = game.pitcher_stat(winner, "wins", winner_side)
            self.winning_pitcher_losses = game.pitcher_stat(winner, "losses", winner_side)
        else:
            self.winning_pitcher = PITCHER_UNKNOWN
            self.winning_pitcher_wins = 0
            self.winning_pitcher_losses = 0

        save = game.decision_pitcher_id("save")
        if save is not None:
            self.save_pitcher = game.full_name(save)
            self.save_pitcher_saves = game.pitcher_stat(save, "saves", winner_side)
        else:
            self.save_pitcher = None
            self.save_pitcher_saves = None

        loser = game.decision_pitcher_id("loser")
        if loser is not None:
            loser_side = game.losing_team()
            self.losing_pitcher = game.full_name(loser)
            self.losing_pitcher_wins = game.pitcher_stat(loser, "wins", loser_side)
            self.losing_pitcher_losses = game.pitcher_stat(loser, "losses", loser_side)
        else:
            self.losing_pitcher = PITCHER_UNKNOWN
            self.losing_pitcher_wins = 0
            self.losing_pitcher_losses = 0

    def __str__(self):
        return "<{} {}> W: {} {}-{}; L: {} {}-{}; S: {} ({})".format(
            self.__class__.__name__,
            hex(id(self)),
            self.winning_pitcher,
            self.winning_pitcher_wins,
            self.winning_pitcher_losses,
            self.losing_pitcher,
            self.losing_pitcher_wins,
            self.losing_pitcher_losses,
            self.save_pitcher,
            self.save_pitcher_saves,
        )
