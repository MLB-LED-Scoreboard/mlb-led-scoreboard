class LiveGamePresenter:
    def __init__(self, game, config):
        self.game = game
        self.config = config

    def count_text(self):
        return "{}-{}".format(self.game.pitches().balls, self.game.pitches().strikes)
    
    def pitcher_text(self):
        pitcher = self.game.pitcher()
        pitch_count = self.config.layout.coords("atbat.pitch_count")

        if pitch_count.enabled and pitch_count.append_pitcher_name:
            pitches = self.game.pitches().curren_pitcher_pitch_count()
            pitcher = f"{pitcher} ({pitches})"

        return pitcher

    def pitch_text(self):
        coords = self.config.layout.coords("atbat.pitch")
        pitches = self.game.pitches()

        if int(pitches.last_pitch_speed) and coords.enabled:
            mph = " "
            if coords.mph:
                mph = "mph "
            if coords.desc_length.lower() == "long":
                pitch_text = str(pitches.last_pitch_speed) + mph + pitches.last_pitch_type_long
            elif coords.desc_length.lower() == "short":
                pitch_text = str(pitches.last_pitch_speed) + mph + pitches.last_pitch_type
            else:
                pitch_text = ""
        
            return pitch_text
