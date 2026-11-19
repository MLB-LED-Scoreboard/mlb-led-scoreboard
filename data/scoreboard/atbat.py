from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.game import Game


class AtBat:
    def __init__(self, game: "Game"):

        self.batter = game.batter()
        self.on_deck = game.on_deck()
        self.in_hole = game.in_hole()
        self.pitcher = game.pitcher()
        self.batter_order = game.batter_batting_order()
        self.on_deck_order = game.on_deck_batting_order()
        self.in_hole_order = game.in_hole_batting_order()
        self.avg = game.batter_stat("avg")
        self.home_runs = game.batter_stat("homeRuns")
        self.rbi = game.batter_stat("rbi")
        self.pitcher_era = game.pitcher_era()
