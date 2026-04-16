from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.game import Game


class Outs:
    def __init__(self, game: "Game"):
        self.number = game.outs()
