import cli
from data.config import Config
from unittest import mock
from pathlib import Path

TEST_CONFIG_PATH = Path(__file__).parent / "fixtures" / "config.example.json"


def make_test_config(**test_overrides):
    """
    Creates a Config object with default values plus any overrides.
    Config path defaults to the fixture in `tests/fixtures/config.example.json`, which simulates
    the `example` fallback behavior in a normal config object.
    """
    _arguments = cli.arguments

    def patched_arguments(overrides={}):
        merged = {**overrides, **test_overrides}
        if merged.get("config", None) is None:
            merged["config"] = TEST_CONFIG_PATH
        return _arguments(overrides=merged)

    with mock.patch.object(cli, "arguments", patched_arguments):
        with mock.patch("bullpen.logging.LOGGER.warning"):
            return Config()
