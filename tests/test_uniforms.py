"""
Tests for the Uniforms module.

statsapi is mocked here so we can exercise the matching logic against synthetic responses.
Note: All special uniform names are fabricated.
"""

import time
import unittest
from unittest.mock import patch

import data.uniforms
from data.uniforms import Uniforms


def _response(home_assets=None, away_assets=None):
    """Build a statsapi.get return value with the given asset text lists."""
    return {
        "uniforms": [
            {
                "home": {"uniformAssets": [{"uniformAssetText": t} for t in (home_assets or [])]},
                "away": {"uniformAssets": [{"uniformAssetText": t} for t in (away_assets or [])]},
            }
        ]
    }


class TestUniforms(unittest.TestCase):
    def test_update_finds_home_special_uniform(self):
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["Mets City Connect Alternate"],
                away_assets=["Standard Road Grey"],
            ),
        ) as mock_get:
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertEqual(u.home_special_uniform(), "city_connect")
        self.assertIsNone(u.away_special_uniform())
        mock_get.assert_called_once()

    def test_update_finds_away_special_uniform(self):
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["Standard Home"],
                away_assets=["City Connect Cap"],
            ),
        ):
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertIsNone(u.home_special_uniform())
        self.assertEqual(u.away_special_uniform(), "city_connect")

    def test_update_no_match(self):
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["Standard Home"],
                away_assets=["Standard Road"],
            ),
        ):
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertIsNone(u.home_special_uniform())
        self.assertIsNone(u.away_special_uniform())

    def test_update_case_insensitive(self):
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["mets CITY connect alternate"],
            ),
        ):
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertEqual(u.home_special_uniform(), "city_connect")

    def test_lambdas_capture_distinct_values_per_uniform_type(self):
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["Memorial Day Stars and Stripes Cap"],
                away_assets=["Mets City Connect Alternate"],
            ),
        ):
            u = Uniforms(
                game_id=1,
                uniform_types={
                    "memorial_day": "Memorial Day",  # first
                    "city_connect": "City Connect",  # last
                },
            )

        self.assertEqual(u.home_special_uniform(), "memorial_day")
        self.assertEqual(u.away_special_uniform(), "city_connect")

    def test_lambdas_directly_match_only_their_own_value(self):
        with patch("data.uniforms.statsapi.get", return_value=_response()):
            u = Uniforms(
                game_id=1,
                uniform_types={
                    "city_connect": "City Connect",
                    "memorial_day": "Memorial Day",
                    "throwback": "1969",
                },
            )

        check_cc = u._special_uniforms["city_connect"]
        check_md = u._special_uniforms["memorial_day"]
        check_tb = u._special_uniforms["throwback"]

        self.assertTrue(check_cc("Mets City Connect"))
        self.assertFalse(check_cc("Memorial Day Cap"))
        self.assertFalse(check_cc("1969 Throwback"))

        self.assertTrue(check_md("Memorial Day Cap"))
        self.assertFalse(check_md("City Connect"))
        self.assertFalse(check_md("1969 Throwback"))

        self.assertTrue(check_tb("1969 Throwback Jersey"))
        self.assertFalse(check_tb("City Connect"))
        self.assertFalse(check_tb("Memorial Day"))

    def test_update_is_idempotent_once_set(self):
        # After the constructor populates home_special, subsequent update() calls
        # should short-circuit and NOT hit the API again.
        first = _response(home_assets=["City Connect"], away_assets=["Standard Road"])
        with patch("data.uniforms.statsapi.get", return_value=first) as mock_get:
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})
            self.assertEqual(mock_get.call_count, 1)

            u.update(force=True)
            u.update(force=True)
            self.assertEqual(mock_get.call_count, 1)

        self.assertEqual(u.home_special_uniform(), "city_connect")
        self.assertIsNone(u.away_special_uniform())

    def test_update_handles_missing_home_away_keys(self):
        with patch("data.uniforms.statsapi.get", return_value={"uniforms": [{}]}):
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertIsNone(u.home_special_uniform())
        self.assertIsNone(u.away_special_uniform())

    def test_update_handles_missing_uniform_assets(self):
        with patch("data.uniforms.statsapi.get", return_value={"uniforms": [{"home": {}, "away": {}}]}):
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertIsNone(u.home_special_uniform())
        self.assertIsNone(u.away_special_uniform())

    def test_update_swallows_api_exception(self):
        with patch("data.uniforms.statsapi.get", side_effect=RuntimeError("FAIL")):
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})

        self.assertIsNone(u.home_special_uniform())
        self.assertIsNone(u.away_special_uniform())

    def test_update_empty_uniform_types(self):
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["City Connect"],
                away_assets=["Memorial Day"],
            ),
        ) as mock_get:
            u = Uniforms(game_id=1, uniform_types={})

        self.assertEqual(mock_get.call_count, 1)
        self.assertIsNone(u.home_special_uniform())
        self.assertIsNone(u.away_special_uniform())

    def test_update_first_matching_type_wins(self):
        # An asset text that contains BOTH configured substrings should resolve
        # to whichever type is iterated first (dict insertion order).
        # Not clear if this is behavior that can actually happen, but codifying it in a test nonetheless.
        with patch(
            "data.uniforms.statsapi.get",
            return_value=_response(
                home_assets=["City Connect Memorial Day Hybrid"],
            ),
        ):
            u = Uniforms(
                game_id=1,
                uniform_types={
                    "city_connect": "City Connect",
                    "memorial_day": "Memorial Day",
                },
            )

        self.assertEqual(u.home_special_uniform(), "city_connect")

    def test_update_throttles_without_force(self):
        with patch("data.uniforms.statsapi.get", return_value=_response()) as mock_get:
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})
            self.assertEqual(mock_get.call_count, 1)

            u.update()  # within UPDATE_RATE -> throttled
            self.assertEqual(mock_get.call_count, 1)

            # Backdate starttime to force the throttle check to allow another call.
            u.starttime = time.time() - (data.uniforms.UPDATE_RATE + 1)
            u.update()
            self.assertEqual(mock_get.call_count, 2)

    def test_force_bypasses_throttle(self):
        with patch("data.uniforms.statsapi.get", return_value=_response()) as mock_get:
            u = Uniforms(game_id=1, uniform_types={"city_connect": "City Connect"})
            self.assertEqual(mock_get.call_count, 1)

            u.update(force=True)
            self.assertEqual(mock_get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
