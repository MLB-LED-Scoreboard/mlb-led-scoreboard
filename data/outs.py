class Outs:
    def __init__(self, game_data):
        self.number = game_data["liveData"]["linescore"].get("outs", 0)
