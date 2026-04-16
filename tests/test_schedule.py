"""
Tests for the Schedule module.

Note: we do **NOT** mock statsapi here, as we want to test the actual data returned from the API.
A similar set of tests with stored responses may be separately added in the future.
"""

import unittest
import unittest.mock
import data.schedule

from tests.helpers import make_test_config


class TestSchedule(unittest.TestCase):
    demo_config = make_test_config(config="tests/data/demo-date-midseason", led_cols=32, led_rows=32)
    schedule = data.schedule.Schedule(demo_config)

    def test_schedule_midseason(self):
        self.assertEqual(self.schedule.num_games(), 15)

    @unittest.mock.patch("data.status.is_live", return_value=True)
    def test_schedule_midseason_preferred(self, mock_is_live):
        self.schedule.update(True)
        gn = self.schedule.next_game()

        self.assertIsNotNone(gn)
        self.assertEqual(gn.home_name(), "Red Sox")

        gm = self.schedule.next_game()
        self.assertIsNotNone(gm)
        self.assertEqual(gm.home_name(), "Nationals")
        # this was a fun game
        self.assertEqual(gm.inning_number(), 14)


class TestSchedulePlayoff(unittest.TestCase):
    demo_config = make_test_config(config="tests/data/demo-date-playoffs", led_cols=32, led_rows=32)
    schedule = data.schedule.Schedule(demo_config)

    def test_schedule_playoff(self):
        self.assertEqual(self.schedule.num_games(), 4)
        # even though the second preferred team is playing, we only care about the first for this
        self.assertIsNotNone(self.schedule.next_game())


class TestScheduleOffday(unittest.TestCase):
    demo_config = make_test_config(config="tests/data/demo-date-offday", led_cols=32, led_rows=32)
    schedule = data.schedule.Schedule(demo_config)

    def test_schedule_offday(self):
        self.assertEqual(self.schedule.num_games(), 0)
        self.assertIsNone(self.schedule.next_game())
