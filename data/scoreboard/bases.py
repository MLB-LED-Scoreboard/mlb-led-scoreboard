class Bases:
    def __init__(self, game_data):
        b1 = None
        b2 = None
        b3 = None

        try:
            b1 = game_data["liveData"]["linescore"]["offense"]["first"]["id"]
        except KeyError:
            pass

        try:
            b2 = game_data["liveData"]["linescore"]["offense"]["second"]["id"]
        except KeyError:
            pass

        try:
            b3 = game_data["liveData"]["linescore"]["offense"]["third"]["id"]
        except KeyError:
            pass

        self.runners = [b1, b2, b3]

    def __str__(self):
        rs = []
        for r in self.runners:
            rs.append("X" if r else " ")
        return "[{}][{}][{}]".format(rs[0], rs[1], rs[2])
