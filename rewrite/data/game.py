from data.status import Status

class Game:

    @staticmethod
    def from_schedule(game_data):
        game = Game(game_data)

        if game.update() == Status.SUCCESS:
            return game

        return None

    def __init__(self, data):
        self._data = data

        self.id = data["game_id"]

    def update(self):
        return Status.SUCCESS
