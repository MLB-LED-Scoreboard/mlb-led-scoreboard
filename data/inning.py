class Inning:

    TOP = "Top"
    BOTTOM = "Bottom"
    MIDDLE = "Middle"
    END = "End"

    def __init__(self, game_data):
        self.number = game_data["liveData"]["linescore"]["currentInning"]
        self.state = game_data["liveData"]["linescore"]["inningState"]
        self.ordinal = game_data["liveData"]["linescore"]["currentInningOrdinal"]
