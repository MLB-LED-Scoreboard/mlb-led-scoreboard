class LiveGamePresenter:
    def __init__(self, game, config):
        self.game = game
        self.config = config

    def batter_count_text(self):
        return "{}-{}".format(self.game.pitches().balls, self.game.pitches().strikes)