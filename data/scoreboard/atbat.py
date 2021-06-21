class AtBat:
    def __init__(self, game_data):
        offense = game_data["liveData"]["linescore"]["offense"]
        try:
            batter_id = "ID" + str(offense["batter"]["id"])
            self.batter = game_data["gameData"]["players"][batter_id]["boxscoreName"]
        except:
            self.batter = ""

        try:
            onDeck_id = "ID" + str(offense["onDeck"]["id"])
            self.onDeck = game_data["gameData"]["players"][onDeck_id]["boxscoreName"]
        except:
            self.onDeck = ""

        try:
            inHole_id = "ID" + str(offense["inHole"]["id"])
            self.inHole = game_data["gameData"]["players"][inHole_id]["boxscoreName"]
        except:
            self.inHole = ""

        try:
            pitcher_id = "ID" + str(game_data["liveData"]["linescore"]["defense"]["pitcher"]["id"])
            self.pitcher = game_data["gameData"]["players"][pitcher_id]["boxscoreName"]
        except:
            self.pitcher = ""
