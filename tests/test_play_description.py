"""Tests for the play-by-play text line.

`Game.current_play_description()` picks the most informative thing available for a
single line of text: the resolved play, else the pitch just thrown, else the last
resolved play held over. The fallbacks matter more than they look -- MLB only
populates `result.description` once an at-bat *ends*, so a layout that used it
alone would sit blank through most of every at-bat.
"""

import unittest

from data.game import Game, _article


def game_with(result_description=None, events=None, players=None, pitcher_id=None):
    """A Game with just enough live data for the description methods."""
    game = Game.__new__(Game)
    current_play = {"result": {}}
    if result_description is not None:
        current_play["result"]["description"] = result_description
    if events is not None:
        current_play["playEvents"] = events
    game._current_data = {
        "liveData": {
            "plays": {"currentPlay": current_play},
            "linescore": {"defense": {"pitcher": {"id": pitcher_id}} if pitcher_id else {}},
        },
        "gameData": {"players": players or {}},
    }
    return game


def pitch(pitch_type="Slider", speed=88.4, call="Ball", is_pitch=True):
    details = {"description": call}
    if pitch_type:
        details["type"] = {"description": pitch_type}
    return {"isPitch": is_pitch, "details": details, "pitchData": {"startSpeed": speed}}


PITCHER = {"ID660271": {"fullName": "Shohei Ohtani", "boxscoreName": "Ohtani, S"}}


class TestArticle(unittest.TestCase):
    """ "a 88mph" reads wrong: spoken, 88 begins with a vowel."""

    def test_eighties_take_an(self):
        self.assertEqual(_article(88), "an")
        self.assertEqual(_article(80), "an")

    def test_other_speeds_take_a(self):
        for speed in (71, 94, 100, 65):
            self.assertEqual(_article(speed), "a", speed)

    def test_vowel_initial_pitch_names_take_an(self):
        self.assertEqual(_article("Eephus"), "an")
        self.assertEqual(_article("Slider"), "a")


class TestLastPitchSentence(unittest.TestCase):
    def test_reads_as_prose(self):
        game = game_with(events=[pitch()], players=PITCHER, pitcher_id=660271)
        self.assertEqual(game.last_pitch_sentence(), "Shohei Ohtani throws an 88mph Slider (Ball)")

    def test_uses_the_last_event_not_the_first(self):
        game = game_with(
            events=[pitch("Curveball", 78, "Called Strike"), pitch("Sinker", 94, "Foul")],
            players=PITCHER,
            pitcher_id=660271,
        )
        self.assertIn("Sinker", game.last_pitch_sentence())
        self.assertNotIn("Curveball", game.last_pitch_sentence())

    def test_in_play_calls_are_omitted(self):
        """The resolved play arrives seconds later and says what happened, so
        announcing "in play, out(s)" first is clumsy and redundant."""
        game = game_with(events=[pitch(call="In play, out(s)")], players=PITCHER, pitcher_id=660271)
        sentence = game.last_pitch_sentence()
        self.assertNotIn("In play", sentence)
        self.assertTrue(sentence.endswith("Slider"), sentence)

    def test_a_call_that_repeats_the_pitch_type_is_omitted(self):
        game = game_with(events=[pitch("Slider", 88, "Slider")], players=PITCHER, pitcher_id=660271)
        self.assertEqual(game.last_pitch_sentence().count("Slider"), 1)

    def test_non_pitch_events_are_ignored(self):
        game = game_with(events=[pitch(is_pitch=False)], players=PITCHER, pitcher_id=660271)
        self.assertEqual(game.last_pitch_sentence(), "")

    def test_no_events_is_empty(self):
        self.assertEqual(game_with(events=[]).last_pitch_sentence(), "")


class TestCurrentPlayDescription(unittest.TestCase):
    def test_a_resolved_play_wins(self):
        game = game_with(
            result_description="Ohtani homers (40) on a fly ball to right field.",
            events=[pitch()],
            players=PITCHER,
            pitcher_id=660271,
        )
        self.assertEqual(game.current_play_description(), "Ohtani homers (40) on a fly ball to right field.")

    def test_falls_back_to_the_live_pitch_mid_at_bat(self):
        game = game_with(events=[pitch()], players=PITCHER, pitcher_id=660271)
        self.assertEqual(game.current_play_description(), "Shohei Ohtani throws an 88mph Slider (Ball)")

    def test_empty_when_there_is_nothing_live(self):
        """Between innings and across a pitching change there is no pitch and no
        result. Nothing is remembered across updates -- a Game is rebuilt often
        enough while rotating that held state would be unreliable anyway."""
        game = game_with(result_description="Ohtani singles on a line drive.", players=PITCHER)
        game.current_play_description()

        game._current_data["liveData"]["plays"]["currentPlay"] = {"result": {}}
        self.assertEqual(game.current_play_description(), "")

    def test_the_live_pitch_wins_once_the_result_is_cleared(self):
        game = game_with(result_description="Ohtani doubles.", players=PITCHER, pitcher_id=660271)
        self.assertEqual(game.current_play_description(), "Ohtani doubles.")

        game._current_data["liveData"]["plays"]["currentPlay"] = {"result": {}, "playEvents": [pitch()]}
        self.assertIn("throws", game.current_play_description())

    def test_empty_when_nothing_has_happened_yet(self):
        self.assertEqual(game_with().current_play_description(), "")


if __name__ == "__main__":
    unittest.main()
