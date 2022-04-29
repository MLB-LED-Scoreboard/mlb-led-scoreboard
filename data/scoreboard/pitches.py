from data.game import Game
import data.pitches

class Pitches:
    def __init__(self, game: Game):
        self.balls = game.balls()
        self.strikes = game.strikes()
        last_pitch = game.last_pitch()
        if last_pitch is None:
            self.last_pitch_speed = "0"
            self.last_pitch_type = "UK"
            self.last_pitch_type_long = "Unknown"
        else:
            self.last_pitch_speed = f"{round(last_pitch[0])}"
            self.last_pitch_type = data.pitches.PITCH_SHORT[last_pitch[1]]
            self.last_pitch_type_long = data.pitches.PITCH_LONG[last_pitch[1]]

    def __str__(self) -> str:
        return f"Count: {self.balls} - {self.strikes}. Last pitch: {self.last_pitch_speed}mph {self.last_pitch_type} {self.last_pitch_long}"
