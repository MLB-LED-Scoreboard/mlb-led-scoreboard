"""
Tests for the Schedule module.

Note: we do **NOT** mock statsapi here, as we want to test the actual data returned from the API.
A similar set of tests with stored responses may be separately added in the future.
"""

import unittest
import unittest.mock
import data.schedule
import data.config


class TestSchedule(unittest.TestCase):
    demo_config = data.config.Config("tests/data/demo-date-midseason", 32, 32)
    schedule = data.schedule.Schedule(demo_config)

    def test_schedule_midseason(self):
        self.assertEqual(self.schedule.num_games(), 15)
        self.assertFalse(self.schedule.is_offday())
        self.assertFalse(self.schedule.is_offday_for_preferred_team())
        # because it's in the past
        self.assertFalse(self.schedule.games_live())

    @unittest.mock.patch("data.status.is_live", return_value=True)
    def test_schedule_midseason_preferred(self, mock_is_live):
        # mock should make this True
        self.assertTrue(self.schedule.games_live())

        gm = self.schedule.get_preferred_game()
        self.assertIsNotNone(gm)
        self.assertEqual(gm.home_name(), "Nationals")
        # this was a fun game
        self.assertEqual(gm.inning_number(), 14)

        gn = self.schedule.next_game()
        self.assertIsNotNone(gn)
        self.assertEqual(gn.home_name(), "Red Sox")


class TestSchedulePlayoff(unittest.TestCase):
    demo_config = data.config.Config("tests/data/demo-date-playoffs", 32, 32)
    schedule = data.schedule.Schedule(demo_config)

    def test_schedule_playoff(self):
        self.assertFalse(self.schedule.is_offday())
        self.assertEqual(self.schedule.num_games(), 4)
        # even though the second preferred team is playing, we only care about the first for this
        self.assertTrue(self.schedule.is_offday_for_preferred_team())
        self.assertIsNotNone(self.schedule.get_preferred_game())


class TestScheduleOffday(unittest.TestCase):
    demo_config = data.config.Config("tests/data/demo-date-offday", 32, 32)
    schedule = data.schedule.Schedule(demo_config)

    def test_schedule_offday(self):
        self.assertTrue(self.schedule.is_offday())
        self.assertEqual(self.schedule.num_games(), 0)
        self.assertTrue(self.schedule.is_offday_for_preferred_team())
        self.assertFalse(self.schedule.games_live())
        self.assertIsNone(self.schedule.get_preferred_game())
