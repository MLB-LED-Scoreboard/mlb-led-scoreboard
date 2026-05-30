from data.config.layout import Layout
from data.scoreboard.team import Team
from renderers.games.teams import can_use_full_team_names

import unittest, string, random

WIDTH = 32
HEIGHT = 32


def make_layout(full=False, shorten_team_name_on_high_line_score=False):
    return Layout(
        {
            "teams": {
                "name": {"full": full},
                "line_score": {"shorten_team_name_on_high_line_score": shorten_team_name_on_high_line_score},
                "record": {},
            },
            "defaults": {"font_name": "4x6"},
        },
        WIDTH,
        HEIGHT,
    )


def make_team(
    abbrev="".join(random.choice(string.ascii_uppercase) for _ in range(3)),
    runs=0,
    name=None,
    hits=0,
    errors=0,
    record="0-0",
    special_uniform=None,
):
    if name is None:
        name = f"Test {abbrev}"

    return Team(abbrev, runs, name, hits, errors, record, special_uniform)


class TestCanUseFullTeamNames(unittest.TestCase):

    def test_global_setting_disabled(self):
        layout = make_layout()
        teams = [make_team(), make_team()]

        self.assertFalse(can_use_full_team_names(layout, teams))

    def test_global_setting_disabled_shorten_disabled_with_10_hits(self):
        layout = make_layout()
        teams = [make_team(hits=10), make_team()]

        self.assertFalse(can_use_full_team_names(layout, teams))

    def test_global_setting_enabled_shorten_disabled_with_10_hits(self):
        layout = make_layout(full=True)
        teams = [make_team(hits=10), make_team()]

        self.assertTrue(can_use_full_team_names(layout, teams))

    def test_settings_enabled_with_10_hits(self):
        layout = make_layout(full=True, shorten_team_name_on_high_line_score=True)
        teams = [make_team(hits=10), make_team()]

        self.assertFalse(can_use_full_team_names(layout, teams))

    def test_settings_enabled_with_10_runs(self):
        layout = make_layout(full=True, shorten_team_name_on_high_line_score=True)
        teams = [make_team(runs=10), make_team()]

        self.assertFalse(can_use_full_team_names(layout, teams))

    def test_settings_enabled_with_10_errors(self):
        layout = make_layout(full=True, shorten_team_name_on_high_line_score=True)
        # A very bad day at the ballpark
        teams = [make_team(errors=10), make_team()]

        self.assertFalse(can_use_full_team_names(layout, teams))

    def test_settings_enabled_with_rhe_less_than_10(self):
        layout = make_layout(full=True, shorten_team_name_on_high_line_score=True)
        teams = [make_team(runs=5, hits=5, errors=5), make_team(runs=5, hits=5, errors=5)]

        self.assertTrue(can_use_full_team_names(layout, teams))
