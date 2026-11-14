"""Tests for the irregular (delayed / postponed / challenge) status screen."""

import unittest

from data import status
from renderers.games import irregular

# A module-level `def __name` is not mangled, but writing `irregular.__name`
# inside a class body would be, so fetch it by string once, out here.
get_text_for_status = getattr(irregular, "__get_text_for_status")


class FakeScoreboard:
    def __init__(self, game_status):
        self.game_status = game_status


def render_text(game_status, short_text=False):
    return get_text_for_status(FakeScoreboard(game_status), short_text)


class TestStatusText(unittest.TestCase):
    """The long-form text is drawn centre-anchored and unclipped, so an
    unexpectedly long string runs into whatever else is on the panel."""

    def test_challenge_statuses_are_shortened_regardless_of_case(self):
        """MLB writes "Manager challenge" but "Umpire Challenge".

        The check used to be case-sensitive, so the capitalised one skipped the
        shorthand and rendered all 16 characters -- 112px of a 128px panel.
        """
        self.assertEqual(render_text("Manager challenge: Home run"), "Challenge")
        self.assertEqual(render_text("Umpire Challenge: Pitch Result"), "Challenge")

    def test_review_statuses_are_shortened_regardless_of_case(self):
        self.assertEqual(render_text("Umpire review: Force play"), "Review")

    def test_delayed_start_collapses_to_delayed(self):
        self.assertEqual(render_text(status.DELAYED_START), status.DELAYED)

    def test_no_irregular_status_renders_longer_than_the_shorthands(self):
        """Nothing should reach the renderer wider than "Suspended" (9 chars).

        The text is centre-anchored at a single `x` and nothing clips it, so a long
        status spreads outwards over whatever else is on the panel. The shorthands
        above are what keep every status inside that budget; this fails if a new one
        slips past them.
        """
        longest = max((render_text(s) for s in status.GAME_STATE_IRREGULAR), key=len)
        self.assertLessEqual(len(longest), 10, f"{longest!r} is too wide for the status column")


if __name__ == "__main__":
    unittest.main()
