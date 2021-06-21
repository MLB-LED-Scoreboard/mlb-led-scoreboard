class Pitches:
    def __init__(self, game_data):
        self.balls = game_data["liveData"]["linescore"].get("balls", 0)
        self.strikes = game_data["liveData"]["linescore"].get("strikes", 0)
