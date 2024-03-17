from utils import format_id, value_at_keypath

class Pitches:

    # A list of mlb pitch types appearing in statcast
    # from statsapi.meta("pitchTypes")
    # Dont change the index, but feel free to change
    # the descriptions

    PITCH_LONG = {
        "AB": "Auto Ball",  # MLB default is "Automatic Ball"
        "AS": "Auto Strike",  # MLB default is "Automatic Strike"
        "CH": "Change-up",
        "CU": "Curveball",
        "CS": "Slow Curve",
        "EP": "Eephus",
        "FC": "Cutter",
        "FA": "Fastball",
        "FF": "Fastball",  # MLB default is "Four-Seam Fastball"
        "FO": "Forkball",
        "FS": "Splitter",
        "FT": "2 Seamer",  # MLB default is "Two-Seam Fastball"
        "GY": "Gyroball",
        "IN": "Int Ball",  # MLB default is "Intentional Ball"
        "KC": "Knuckle Curve",
        "KN": "Knuckleball",
        "NP": "No Pitch",
        "PO": "Pitchout",
        "SC": "Screwball",
        "SI": "Sinker",
        "SL": "Slider",
        "ST": "Sweeper",
        "SV": "Slurve",
        "UN": "Unknown",
    }

    PITCH_SHORT = {
        "AB": "AB",
        "AS": "AS",
        "CH": "CH",
        "CU": "CU",
        "CS": "CS",
        "EP": "EP",
        "FC": "FC",
        "FA": "FA",
        "FF": "FF",
        "FO": "FO",
        "FS": "FS",
        "FT": "FT",
        "GY": "GY",
        "IN": "IN",
        "KC": "KC",
        "KN": "KN",
        "NP": "NP",
        "PO": "PO",
        "SC": "SC",
        "SI": "SI",
        "SL": "SL",
        "SV": "SV",
        "ST": "SW", # MLB default is "ST"
        "UN": "UN",
    }

    def __init__(self, game):
        self.game = game

        self.balls = self.balls()
        self.strikes = self.strikes()
        self.pitch_count = self.current_pitcher_pitch_count()

        last_pitch = self.last_pitch()
        self.last_pitch_speed = "0"
        self.last_pitch_type = Pitches.PITCH_SHORT["UN"]
        self.last_pitch_type_long = Pitches.PITCH_LONG["UN"]

        if last_pitch:
            self.last_pitch_speed = f"{round(last_pitch[0])}"
            self.last_pitch_type = Pitches.fetch_short(last_pitch[1])
            self.last_pitch_type_long = Pitches.fetch_long(last_pitch[1])

    def balls(self):
        return self.__fetch_count_part("balls")

    def strikes(self):
        return self.__fetch_count_part("strikes")

    def last_pitch(self):
        # TODO: Clean this up.
        try:
            play = self.game.data["liveData"]["plays"].get("currentPlay", {}).get("playEvents", [{}])[-1]
            if play.get("isPitch", False):
                return (
                    play["pitchData"].get("startSpeed", 0),
                    play["details"]["type"]["code"],
                    play["details"]["type"]["description"],
                )
        except:
            return None
    
    def current_pitcher_pitch_count(self):
        # TODO: Clean this up
        try:
            pitcher_id = self.game.data["liveData"]["linescore"]["defense"]["pitcher"]["id"]

            # TODO: ID formatting probably doesn't belong on Game object if it's being used here
            ID = format_id(pitcher_id)
            try:
                return self.game.data["liveData"]["boxscore"]["teams"]["away"]["players"][ID]["stats"]["pitching"][
                    "numberOfPitches"
                ]
            except:
                return self.game.data["liveData"]["boxscore"]["teams"]["home"]["players"][ID]["stats"]["pitching"][
                    "numberOfPitches"
                ]
        except:
            return 0
    
    def __fetch_count_part(self, part):
        return value_at_keypath(self.game.data, "liveData.linescore").get(part, 0)

    @staticmethod
    def fetch_long(value):
        return Pitches.PITCH_LONG.get(value, Pitches.PITCH_LONG["UN"])

    @staticmethod
    def fetch_short(value):
        return Pitches.PITCH_SHORT.get(value, Pitches.PITCH_SHORT["UN"])

    def __str__(self) -> str:
        return (
            f"Count: {self.balls} - {self.strikes}. "
            + f"Last pitch: {self.last_pitch_speed}mph {self.last_pitch_type} {self.last_pitch_type_long} "
            + f" Total pitches: {self.pitch_count}"
        )
