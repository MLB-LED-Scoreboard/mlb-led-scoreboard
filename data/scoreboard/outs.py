from data.game import Game


class Outs:
    def __init__(self, game: Game):
        self.number = game.outs()
