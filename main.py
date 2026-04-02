import sys

import debug

if sys.version_info < (3, 10):
    debug.error("Please run with Python >= 3.10")
    sys.exit(1)

import statsapi

statsapi_version = tuple(map(int, statsapi.__version__.split(".")))
if statsapi_version < (1, 9, 0):
    debug.error("We require MLB-StatsAPI 1.9.0 or higher. You may need to re-run install.sh")
    sys.exit(1)

import logging
import os
import threading
import time

from PIL import Image
from pathlib import Path

# Important! Import the driver first to initialize it, then import submodules as needed.
import driver
from driver import RGBMatrix, __version__

from cli import ScoreboardCLI
from data import Data
from data.config import Config
from renderers.main import MainRenderer
from version import SCRIPT_NAME, SCRIPT_VERSION


def main(matrix, config):
    # Set the scoreboard logger
    logger = logging.getLogger("mlbled")
    if config.debug:
        logger.setLevel(logging.DEBUG)
        if config.debug == "with-statsapi":
            # Assign the scoreboard logger to statsapi
            statsapi.logger = logger
    else:
        logger.setLevel(logging.WARNING)

    # Print some basic info on startup
    debug.info("%s - v%s (%sx%s)", SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height)

    if driver.is_emulated():
        if driver.hardware_load_failed:
            debug.log("rgbmatrix not installed, falling back to emulator!")

        debug.log("Using RGBMatrixEmulator version %s", __version__)
    else:
        debug.log("Using rgbmatrix version %s", __version__)

    # Draw startup screen
    logo_filename = "mlb-w{}h{}.png".format(matrix.width, matrix.height)
    logo_path = (Path(__file__).parent / "assets" / logo_filename).resolve()

    # MLB image disabled when using renderer, for now.
    # see: https://github.com/ty-porter/RGBMatrixEmulator/issues/9#issuecomment-922869679
    if os.path.exists(logo_path) and driver.is_hardware():
        logo = Image.open(logo_path)
        matrix.SetImage(logo.convert("RGB"))
        logo.close()

    # Create a new data object to manage the MLB data
    # This will fetch initial data from MLB
    data = Data(config)

    # create render thread
    render = threading.Thread(target=__render_main, args=[matrix, data], name="render_thread", daemon=True)
    time.sleep(1)
    render.start()

    while render.is_alive():
        time.sleep(0.1)
        data.refresh_schedule()
        time.sleep(0.1)
        if data.schedule.num_games():
            data.refresh_game()
        time.sleep(0.1)
        if data.config.screen_time_at_priority("standings", data.schedule.priority):
            data.refresh_standings()
        time.sleep(0.2)
        if data.config.screen_time_at_priority("news", data.schedule.priority):
            data.refresh_news_ticker()
            data.refresh_weather()


def __render_main(matrix, data):
    MainRenderer(matrix, data).render()


if __name__ == "__main__":
    cli = ScoreboardCLI()
    config = Config(cli.arguments())

    if driver.is_emulated():
        config.matrix_options.emulator_title = f"{SCRIPT_NAME} v{SCRIPT_VERSION}"
        config.matrix_options.icon_path = (Path(__file__).parent / "assets" / "mlb-emulator-icon.png").resolve()

    matrix = RGBMatrix(options=config.matrix_options)

    try:
        main(matrix, config)
    except:
        debug.exception("Untrapped error in main!")
        sys.exit(1)
    finally:
        matrix.Clear()
