from data.config import Config
from utils import args
from unittest import mock
from pathlib import Path

TEST_CONFIG_PATH = Path(__file__).parent / "fixtures" / "config.example.json"

def make_test_config(**kwargs):
    '''
    Creates a Config object with default values plus any overrides.
    Config path defaults to the fixture in `tests/fixtures/config.example.json`, which simulates
    the `example` fallback behavior in a normal config object.

    Note: This reads from ARGV, however this shouldn't be an issue because matrix-specific flags
    shouldn't be used to initialize tests.
    '''
    clargs = args()

    for flag, value in kwargs.items():
        clargs.__setattr__(flag, value)

    if kwargs.get("config", None) is None:
        clargs.config = TEST_CONFIG_PATH

    with mock.patch("debug.warning"):
        return Config(clargs)
