import statsapi

UNKNOWN = "Unknown"


class Final:
    def __init__(self, game_data):

        try:
            w_id = "ID" + str(game_data["liveData"]["decisions"]["winner"]["id"])
            self.winning_pitcher = game_data["liveData"]["decisions"]["winner"]["fullName"]
            try:
                w_stats = game_data["liveData"]["boxscore"]["teams"]["home"]["players"][w_id]["seasonStats"]["pitching"]
                self.winning_team = game_data["gameData"]["teams"]["home"]["teamName"]
            except:
                w_stats = game_data["liveData"]["boxscore"]["teams"]["away"]["players"][w_id]["seasonStats"]["pitching"]
                self.winning_team = game_data["gameData"]["teams"]["away"]["teamName"]

            self.winning_pitcher_wins = w_stats["wins"]
            self.winning_pitcher_losses = w_stats["losses"]
        except:
            self.winning_team = UNKNOWN
            self.winning_pitcher = UNKNOWN
            self.winning_pitcher_wins = 0
            self.winning_pitcher_losses = 0

        try:
            l_id = "ID" + str(game_data["liveData"]["decisions"]["loser"]["id"])
            self.losing_pitcher = game_data["liveData"]["decisions"]["loser"]["fullName"]

            try:
                l_stats = game_data["liveData"]["boxscore"]["teams"]["home"]["players"][l_id]["seasonStats"]["pitching"]
                self.losing_team = game_data["gameData"]["teams"]["home"]["teamName"]

            except:
                l_stats = game_data["liveData"]["boxscore"]["teams"]["away"]["players"][l_id]["seasonStats"]["pitching"]
                self.losing_team = game_data["gameData"]["teams"]["away"]["teamName"]

            self.losing_pitcher_wins = l_stats["wins"]
            self.losing_pitcher_losses = l_stats["losses"]
        except:
            self.losing_team = UNKNOWN
            self.losing_pitcher = UNKNOWN
            self.losing_pitcher_wins = 0
            self.losing_pitcher_losses = 0

        try:
            s_id = "ID" + str(game_data["liveData"]["decisions"]["save"]["id"])
            self.save_pitcher = game_data["liveData"]["decisions"]["save"]["fullName"]
            try:
                self.save_pitcher_saves = game_data["liveData"]["boxscore"]["teams"]["home"]["players"][s_id][
                    "seasonStats"
                ]["pitching"]["saves"]
            except:
                self.save_pitcher_saves = game_data["liveData"]["boxscore"]["teams"]["away"]["players"][s_id][
                    "seasonStats"
                ]["pitching"]["saves"]
        except:
            self.save_pitcher = None
            self.save_pitcher_saves = None

    def __str__(self):
        return "<{} {}> W: {} {}-{} ({}); L: {} {}-{} ({}); S: {} ({})".format(
            self.__class__.__name__,
            hex(id(self)),
            self.winning_pitcher,
            self.winning_pitcher_wins,
            self.winning_pitcher_losses,
            self.winning_team,
            self.losing_pitcher,
            self.losing_pitcher_wins,
            self.losing_pitcher_losses,
            self.losing_team,
            self.save_pitcher,
            self.save_pitcher_saves,
        )
