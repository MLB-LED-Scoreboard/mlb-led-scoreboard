from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.game import Game


class AtBat:
    def __init__(self, game: "Game"):

        self.batter = game.batter()
        self.onDeck = game.on_deck()
        self.inHole = game.in_hole()
        self.pitcher = game.pitcher()
        self.batting_order = game.batter_batting_order()
        self.avg = game.batter_stat("avg")
        self.home_runs = game.batter_stat("homeRuns")
        self.rbi = game.batter_stat("rbi")
        self.pitcher_era = game.pitcher_era()
