"""Tests for the boxscore lookups behind the batter/pitcher stat lines.

All four read `liveData.boxscore.teams.<side>.players.ID<id>`, and none of them
knows which side the player is on -- the linescore gives an id, not a team. So each
tries both sides and takes the first hit. These tests pin that down, along with the
two data quirks that are easy to get wrong:

  * `battingOrder` is a 3-digit *string*: "800" is the 8th spot, and a pinch hitter
    in that spot is "801". The spot is the hundreds digit.
  * every one of these is missing for long stretches of a real game -- before
    lineups are posted, between innings, mid pitching change -- so returning None
    rather than raising is the contract, not a nicety.
"""

import unittest

from data.game import Game


def game_with(players=None, batter_id=None, pitcher_id=None, side="home"):
    """A Game with just enough live data for the boxscore lookups."""
    game = Game.__new__(Game)
    offense = {"batter": {"id": batter_id}} if batter_id is not None else {}
    defense = {"pitcher": {"id": pitcher_id}} if pitcher_id is not None else {}
    game._current_data = {
        "liveData": {
            "linescore": {"offense": offense, "defense": defense},
            "boxscore": {"teams": {"away": {"players": {}}, "home": {"players": {}}}},
        }
    }
    game._current_data["liveData"]["boxscore"]["teams"][side]["players"] = players or {}
    return game


BATTER = {
    "ID12345": {
        "battingOrder": "300",
        "seasonStats": {"batting": {"avg": ".327", "homeRuns": 39, "rbi": 85}},
    }
}
PITCHER = {"ID660271": {"seasonStats": {"pitching": {"era": "3.73"}}}}


class TestBatterStat(unittest.TestCase):
    def test_reads_the_season_batting_line(self):
        game = game_with(players=BATTER, batter_id=12345)
        self.assertEqual(game.batter_stat("avg"), ".327")
        self.assertEqual(game.batter_stat("homeRuns"), 39)
        self.assertEqual(game.batter_stat("rbi"), 85)

    def test_finds_a_batter_on_the_away_side_too(self):
        """The linescore says who is batting, not which team they are on."""
        game = game_with(players=BATTER, batter_id=12345, side="away")
        self.assertEqual(game.batter_stat("avg"), ".327")

    def test_an_unknown_stat_is_none_rather_than_an_error(self):
        game = game_with(players=BATTER, batter_id=12345)
        self.assertIsNone(game.batter_stat("triples"))

    def test_no_batter_yet_is_none(self):
        self.assertIsNone(game_with().batter_stat("avg"))

    def test_a_batter_missing_from_the_boxscore_is_none(self):
        self.assertIsNone(game_with(players=BATTER, batter_id=999).batter_stat("avg"))


class TestBattingOrder(unittest.TestCase):
    def test_the_spot_is_the_hundreds_digit(self):
        game = game_with(players=BATTER, batter_id=12345)
        self.assertEqual(game.batter_batting_order(), 3)

    def test_a_substitute_keeps_the_spot_they_batted_in(self):
        """ "801" is a pinch hitter in the 8 spot, and 8 is what belongs on screen."""
        players = {"ID1": {"battingOrder": "801"}}
        self.assertEqual(game_with(players=players, batter_id=1).batter_batting_order(), 8)

    def test_a_player_with_no_batting_order_is_none(self):
        """Pitchers in a DH game, and anyone before the lineup is posted."""
        players = {"ID1": {"seasonStats": {"batting": {}}}}
        self.assertIsNone(game_with(players=players, batter_id=1).batter_batting_order())

    def test_a_non_numeric_batting_order_is_none(self):
        players = {"ID1": {"battingOrder": ""}}
        self.assertIsNone(game_with(players=players, batter_id=1).batter_batting_order())

    def test_no_player_id_is_none(self):
        self.assertIsNone(game_with().batting_order_for(None))

    def test_on_deck_and_in_hole_use_their_own_linescore_slots(self):
        players = {"ID1": {"battingOrder": "100"}, "ID2": {"battingOrder": "200"}}
        game = game_with(players=players)
        game._current_data["liveData"]["linescore"]["offense"] = {
            "onDeck": {"id": 1},
            "inHole": {"id": 2},
        }
        self.assertEqual(game.on_deck_batting_order(), 1)
        self.assertEqual(game.in_hole_batting_order(), 2)
        # Nobody is at the plate in this data, which must not become a 0.
        self.assertIsNone(game.batter_batting_order())


class TestPitcherEra(unittest.TestCase):
    def test_returns_a_string_so_it_can_be_drawn_directly(self):
        game = game_with(players=PITCHER, pitcher_id=660271)
        self.assertEqual(game.pitcher_era(), "3.73")

    def test_no_pitcher_yet_is_none(self):
        self.assertIsNone(game_with().pitcher_era())

    def test_a_pitcher_with_no_pitching_line_is_none(self):
        players = {"ID660271": {"seasonStats": {}}}
        self.assertIsNone(game_with(players=players, pitcher_id=660271).pitcher_era())


if __name__ == "__main__":
    unittest.main()
