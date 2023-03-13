from data.game import Game
import data.pitches


class Pitches:
    def __init__(self, game: Game):
        self.balls = game.balls()
        self.strikes = game.strikes()
        self.pitch_count = game.current_pitcher_pitch_count()
        last_pitch = game.last_pitch()
        if last_pitch is None:
            self.last_pitch_speed = "0"
            self.last_pitch_type = data.pitches.PITCH_SHORT["UN"]
            self.last_pitch_type_long = data.pitches.PITCH_LONG["UN"]
        else:
            self.last_pitch_speed = f"{round(last_pitch[0])}"
            self.last_pitch_type = data.pitches.fetch_short(last_pitch[1])
            self.last_pitch_type_long = data.pitches.fetch_long(last_pitch[1])

    def __str__(self) -> str:
        return (
            f"Count: {self.balls} - {self.strikes}. "
            + f"Last pitch: {self.last_pitch_speed}mph {self.last_pitch_type} {self.last_pitch_long} "
            + f" Total pitches: {self.pitch_count}"
        )
