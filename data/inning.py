class Inning:

    TOP = "Top"
    BOTTOM = "Bottom"
    MIDDLE = "Middle"
    END = "End"

    def __init__(self, game_data):
        self.number = game_data["liveData"]["linescore"].get("currentInning", 0)
        self.state = game_data["liveData"]["linescore"].get("inningState", "Middle")
        self.ordinal = game_data["liveData"]["linescore"].get("currentInningOrdinal", 0)
