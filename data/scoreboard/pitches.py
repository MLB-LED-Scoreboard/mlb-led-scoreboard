from data.game import Game


class Pitches:
    def __init__(self, game: Game):
        self.balls = game.balls()
        self.strikes = game.strikes()
