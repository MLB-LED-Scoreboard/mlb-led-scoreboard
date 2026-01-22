import sys

from data.screens import ScreenType
import debug

if sys.version_info < (3, 9):
    debug.error("Please run with Python >= 3.9")
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
from utils import args, led_matrix_options

from data import Data
from data.config import Config
from renderers.main import MainRenderer
from version import SCRIPT_NAME, SCRIPT_VERSION


def main(matrix, config_base):

    # Read scoreboard options from config.json if it exists
    config = Config(config_base, matrix.width, matrix.height)
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

    screen = data.get_screen_type()
    if screen == ScreenType.ALWAYS_NEWS:
        __refresh_news(render, data)
    elif screen == ScreenType.ALWAYS_STANDINGS:
        __refresh_standings(render, data)
    elif screen == ScreenType.LEAGUE_OFFDAY or screen == ScreenType.PREFERRED_TEAM_OFFDAY:
        __refresh_offday(render, data)
    else:
        __refresh_gameday(render, data)


def __refresh_news(render_thread, data):  # type: (threading.Thread, Data) -> None
    debug.log("Main has selected the news to refresh")
    while render_thread.is_alive():
        time.sleep(30)
        data.refresh_weather()
        data.refresh_news_ticker()


def __refresh_standings(render_thread, data):  # type: (threading.Thread, Data) -> None
    if data.standings.populated():
        debug.log("Main has selected the standings to refresh")
        while render_thread.is_alive():
            time.sleep(30)
            data.refresh_standings()
    else:
        __refresh_news(render_thread, data)


def __refresh_offday(render_thread, data):  # type: (threading.Thread, Data) -> None
    debug.log("Main has selected the offday information to refresh")
    while render_thread.is_alive():
        time.sleep(30)
        data.refresh_standings()
        data.refresh_weather()
        data.refresh_news_ticker()


def __refresh_gameday(render_thread, data):  # type: (threading.Thread, Data) -> None
    debug.log("Main has selected the gameday information to refresh")

    starttime = time.time()

    while render_thread.is_alive():
        time.sleep(0.5)
        data.refresh_schedule()
        if not data.schedule.games_live():
            cont = False
            if data.config.standings_no_games:
                data.refresh_standings()
                cont = True
            if data.config.news_no_games:
                data.refresh_news_ticker()
                data.refresh_weather()
                cont = True
            if cont:
                continue

        elif data.current_game is None:
            # make sure a game is populated
            data.advance_to_next_game()

        if data.should_rotate_to_next_game():
            if data.scrolling_finished:
                time_delta = time.time() - starttime
                rotate_rate = data.config.rotate_rate_for_status(data.current_game.status())
                if time_delta >= rotate_rate:
                    starttime = time.time()
                    data.advance_to_next_game()
        else:
            data.refresh_game()


def __render_main(matrix, data):
    MainRenderer(matrix, data).render()


if __name__ == "__main__":
    # Check for led configuration arguments
    command_line_args = args()
    matrixOptions = led_matrix_options(command_line_args)

    if driver.is_emulated():
        matrixOptions.emulator_title = f"{SCRIPT_NAME} v{SCRIPT_VERSION}"
        matrixOptions.icon_path = (Path(__file__).parent / "assets" / "mlb-emulator-icon.png").resolve()

    # Initialize the matrix
    matrix = RGBMatrix(options=matrixOptions)
    try:
        config, _ = os.path.splitext(command_line_args.config)
        main(matrix, config)
    except:
        debug.exception("Untrapped error in main!")
        sys.exit(1)
    finally:
        matrix.Clear()
