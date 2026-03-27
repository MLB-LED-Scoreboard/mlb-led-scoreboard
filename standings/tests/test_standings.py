"""
Tests for the Standings module.

Note: we do **NOT** mock statsapi here, as we want to test the actual data returned from the API.
A similar set of tests with stored responses may be separately added in the future.
"""

import unittest

import data.config
from mlb_led_scoreboard_standings import standings



class TestStandings(unittest.TestCase):
    demo_config = data.config.Config("tests/data/demo-date-midseason", 32, 32)
    standings = standings.Standings(demo_config)

    def test_standings_midseason(self):
        self.assertFalse(self.standings.is_postseason())
        self.assertTrue(self.standings.populated())

        east = self.standings.current_standings()
        self.assertEqual(east.name, "NL East")
        self.assertEqual(len(east.teams), 5)
        self.assertEqual(east.teams[0].team_abbrev, "ATL")
        self.assertFalse(east.teams[0].clinched)

        self.assertEqual(east.teams[1].team_abbrev, "WSH")
        self.assertEqual(east.teams[1].w, 66)
        self.assertEqual(east.teams[1].l, 56)
        self.assertEqual(east.teams[1].gb, "5.5")

        self.assertEqual(east.teams[2].team_abbrev, "PHI")
        self.assertEqual(east.teams[3].team_abbrev, "NYM")
        self.assertEqual(east.teams[4].team_abbrev, "MIA")
        self.assertFalse(east.teams[4].elim)

        nlwc = self.standings.advance_to_next_standings()
        self.assertEqual(nlwc.name, "NL Wild Card")
        self.assertEqual(len(nlwc.teams), 5)

        self.assertEqual(nlwc.teams[0].team_abbrev, "WSH")
        self.assertEqual(nlwc.teams[0].w, 66)
        self.assertEqual(nlwc.teams[0].l, 56)
        self.assertEqual(nlwc.teams[0].gb, "+1.5")

        self.assertEqual(nlwc.teams[1].team_abbrev, "CHC")
        self.assertEqual(nlwc.teams[1].gb, "-")


class TestSchedulePlayoff(unittest.TestCase):
    demo_config = data.config.Config("tests/data/demo-date-playoffs", 32, 32)
    standings = standings.Standings(demo_config)
    americanBracket = """\
 KC ---|
       |---  KC ---|
DET ---|           | --- NYY ---|
            CLE ---|            |
DET ---|                        | NYY
       |--- DET ---|            |
HOU ---|           | --- CLE ---|
            NYY ---|"""

    def test_standings_playoffs(self):
        self.assertTrue(self.standings.is_postseason())
        self.assertTrue(self.standings.populated())

        AL = self.standings.leagues["AL"]
        self.assertEqual(AL.name, "AL")
        self.assertEqual(str(AL).rstrip(), self.americanBracket)


class TestStandingsEndOfSeason(unittest.TestCase):
    demo_config = data.config.Config("tests/data/demo-date-end", 32, 32)
    date = standings.get_playoff_start_date(2024)  # Note: intentionally wrong year so that the playoff start is in the future
    standings = standings.Standings(demo_config)
    standings.playoffs_start_date = date
    standings.update(force=True)

    def test_standings_end(self):
        self.assertFalse(self.standings.is_postseason())
        self.assertTrue(self.standings.populated())

        # east
        for team in self.standings.current_standings().teams:
            # self.assertTrue(team.clinched or team.elim) # TODO reinstate after API updates
            self.assertFalse(team.clinched and team.elim)

        # wc
        for team in self.standings.advance_to_next_standings().teams:
            # self.assertTrue(team.clinched or team.elim) # TODO reinstate after API updates
            self.assertFalse(team.clinched and team.elim)
