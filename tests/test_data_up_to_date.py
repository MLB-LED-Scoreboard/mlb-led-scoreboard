import unittest
import statsapi
import data.status
import data.teams
import data.pitches


class TestStoredDataUpToDate(unittest.TestCase):
    def test_status_complete(self):
        official_statuses = set(s["detailedState"] for s in statsapi.meta("gameStatus"))
        our_statuses = (
            set(data.status.GAME_STATE_LIVE)
            | set(data.status.GAME_STATE_COMPLETE)
            | set(data.status.GAME_STATE_PREGAME)
            | set(data.status.GAME_STATE_IRREGULAR)
        )
        self.assertSetEqual(official_statuses, our_statuses)

    def test_teams_complete(self):
        teams = statsapi.get("teams", {"sportIds": 1})["teams"]

        abbr_to_full = {t["teamName"]: t["name"] for t in teams}
        self.assertEqual(abbr_to_full, data.teams.TEAM_FULL)
        full_to_abbr = {t["name"]: t["abbreviation"] for t in teams}
        self.assertEqual(full_to_abbr, data.teams.TEAM_ABBR_LN)

    def test_pitches_complete(self):
        pitches = set(p["code"] for p in statsapi.meta("pitchTypes"))
        self.assertSetEqual(pitches, set(data.pitches.PITCH_SHORT.keys()))
        self.assertSetEqual(pitches, set(data.pitches.PITCH_LONG.keys()))

    def test_results_exist(self):
        events = set(e["code"] for e in statsapi.meta("eventTypes"))
        events.add("strikeout_looking") # our custom event
        self.assertTrue(events.issuperset(data.plays.PLAY_RESULTS.keys()))


if __name__ == "__main__":
    unittest.main()
