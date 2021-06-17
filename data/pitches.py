class Pitches:
    def __init__(self, game_data):
        self.balls = game_data["liveData"]["linescore"]["balls"]
        self.strikes = game_data["liveData"]["linescore"]["strikes"]
