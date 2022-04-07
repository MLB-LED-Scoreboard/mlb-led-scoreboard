from data.game import Game


class Bases:
    def __init__(self, game: Game):
        b1 = game.man_on("first")
        b2 = game.man_on("second")
        b3 = game.man_on("third")

        self.runners = [b1, b2, b3]

    def __str__(self):
        rs = []
        for r in self.runners:
            rs.append("X" if r else " ")
        return "[{}][{}][{}]".format(rs[0], rs[1], rs[2])
