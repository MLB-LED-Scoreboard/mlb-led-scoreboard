"""
Tests for the Game module.

Note: we do **NOT** mock statsapi here, as we want to test the actual data returned from the API.
A similar set of tests with stored responses may be separately added in the future.
"""


import unittest
import unittest.mock
import data.game
import data.config
from data.update import UpdateStatus


class TestGame(unittest.TestCase):
    game_data = {
        "game_id": 565956,
        "game_date": "2019-08-17",
        "national_broadcasts": ["FS1"],
        "series_status": "Series tied 1-1",
    }

    def test_game(self):
        game = data.game.Game.from_scheduled(self.game_data, delay=0)
        self.assertIsNotNone(game)
        self.assertEqual(game.home_name(), "Nationals")
        self.assertEqual(game.home_abbreviation(), "WSH")
        self.assertEqual(game.away_name(), "Brewers")
        self.assertEqual(game.away_abbreviation(), "MIL")

        self.assertEqual(game.status(), "Final")
        self.assertEqual(game.inning_number(), 14)
        self.assertEqual(game.inning_state(), "Bottom")
        self.assertEqual(game.inning_ordinal(), "14th")
        self.assertEqual(game.home_score(), 14)
        self.assertEqual(game.away_score(), 15)
        self.assertEqual(game.winning_team(), "away")
        self.assertEqual(game.losing_team(), "home")
        self.assertIsNone(game.decision_pitcher_id("save"))
        self.assertEqual(game.full_name(game.decision_pitcher_id("winner")), "Junior Guerra")
        self.assertEqual(game.full_name(game.decision_pitcher_id("loser")), "Javy Guerra")

        self.assertEqual(game.pitcher(), "Guerra, J")
        self.assertEqual(game.batter(), "Ross")
        self.assertEqual(game.on_deck(), "Suzuki")
        self.assertEqual(game.in_hole(), "Robles")
        self.assertEqual(game.last_pitch(), (94.2, "SI", "Sinker"))
        self.assertEqual(game.current_play_result(), "strikeout")

        self.assertEqual(game.pregame_weather(), "Partly Cloudy and 88° wind 5 mph, Out To LF")
        self.assertEqual(game.broadcasts(), ["FS1"])
        self.assertEqual(game.series_status(), "Series tied 1-1")

        self.assertEqual(game.current_delay(), 0)

    def test_game_in_middle(self):
        # uses some timestamps to test specific points in the game and our delay logic

        game = data.game.Game.from_scheduled(self.game_data, delay=1)
        self.assertIsNotNone(game)
        self.assertEqual(game.current_delay(), 0)

        self.assertEqual(game.update(force=True, testing_params={"timecode": "20190817_230958"}), UpdateStatus.SUCCESS)
        self.assertEqual(game.current_delay(), 10)
        # at this point, should still be 'delayed' (meaning the data is from the end of the game)
        self.assertEqual(game.status(), "Final")

        # Yelich hits a single at this timestamp, but we can't observe it yet
        self.assertEqual(game.update(force=True, testing_params={"timecode": "20190817_231033"}), UpdateStatus.SUCCESS)
        self.assertEqual(game.current_delay(), 10)

        self.assertEqual(game.status(), "In Progress")
        self.assertEqual(game.inning_number(), 1)
        self.assertEqual(game.current_play_result(), "")
        self.assertEqual(game.batter(), "Yelich")
        self.assertFalse(game.man_on('first'))
        self.assertEqual(game.last_pitch(), (83.5, 'FS', 'Splitter'))
        self.assertEqual(game.current_pitcher_pitch_count(), 11)


        # Now we force the second 'live' update
        # (it doesn't matter that this fetch will be at the end of the game!)
        self.assertEqual(game.update(force=True), UpdateStatus.SUCCESS)

        self.assertEqual(game.status(), "In Progress")
        self.assertEqual(game.inning_number(), 1)
        self.assertEqual(game.current_play_result(), "single")
        self.assertTrue(game.man_on('first'))
        self.assertEqual(game.last_pitch(), (88.6, 'FC', 'Cutter'))
        self.assertEqual(game.current_pitcher_pitch_count(), 12)
