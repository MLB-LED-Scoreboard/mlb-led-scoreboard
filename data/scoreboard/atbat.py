from data.game import Game


class AtBat:
    def __init__(self, game: Game):

        self.batter = game.batter()
        self.onDeck = game.on_deck()
        self.inHole = game.in_hole()
        self.pitcher = game.pitcher()
        self.pitcher_pitch_count = game.pitcher_pitch_count()
