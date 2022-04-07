from data.game import Game


class Inning:

    TOP = "Top"
    BOTTOM = "Bottom"
    MIDDLE = "Middle"
    END = "End"

    def __init__(self, game: Game):
        self.number = game.inning_number()
        self.state = game.inning_state()
        self.ordinal = game.inning_ordinal()
