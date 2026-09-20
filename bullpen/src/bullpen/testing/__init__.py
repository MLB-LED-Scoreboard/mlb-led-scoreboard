import bullpen
from datetime import datetime


def make_test_config(
    *, plugin_config: dict = dict(), is_postseason: bool = False, demo_date=None
) -> bullpen.api.config.MLBConfig:
    """
    Creates a Config object with default values plus any overrides.
    Config path defaults to the fixture in `tests/fixtures/config.example.json`, which simulates
    the `example` fallback behavior in a normal config object.
    """

    class TestConfig(bullpen.api.config.MLBConfig):
        scrolling_speed = 1.0
        time_format = "%I:%M %p"

        @property
        def plugin_config(self) -> dict:
            return plugin_config

        def is_postseason(self) -> bool:
            return is_postseason

        def parse_today(self) -> datetime.date:
            if demo_date:
                today = datetime.strptime(demo_date, "%Y-%m-%d")
            else:
                today = datetime.today()
            return today.date()

    return TestConfig()
