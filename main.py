import sys

from data.screens import ScreenType
import debug

if sys.version_info <= (3, 5):
    debug.error("Please run with python3")
    sys.exit(1)

import statsapi

statsapi_version = tuple(map(int, statsapi.__version__.split(".")))
if statsapi_version < (1, 5, 1):
    debug.error("We require MLB-StatsAPI 1.5.1 or higher. You may need to re-run install.sh")
    sys.exit(1)
elif statsapi_version < (1, 6, 1):
    debug.warning("We recommend MLB-StatsAPI 1.6.1 or higher. You may want to re-run install.sh")

import logging
import os
import threading
import time

# TODO: This code addresses CVE-2023-4863 in Pillow < 10.0.1, which requires Python 3.8+
#   See requirements.txt for rationale.
try:
    from PIL import Image

    pil_version = tuple(map(int, Image.__version__.split(".")))
    if pil_version < (10, 0, 1):
        debug.warning(f"Attempted to load an insecure PIL version ({Image.__version__}). We require PIL 10.0.1 or higher.")

        raise ModuleNotFoundError

    PIL_LOADED = True
except:
    debug.warning("PIL failed to load -- images will not be displayed.")
    PIL_LOADED = False

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
    logger = logging.getLogger("mlbled")
    if config.debug:
        logger.setLevel(logging.DEBUG)
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
    logo = "assets/mlb-w" + str(matrix.width) + "h" + str(matrix.height) + ".png"

    # MLB image disabled when using renderer, for now.
    # see: https://github.com/ty-porter/RGBMatrixEmulator/issues/9#issuecomment-922869679
    if os.path.exists(logo) and driver.is_hardware() and PIL_LOADED:
        logo = Image.open(logo)
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
    promise_game = data.schedule.games_live()

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

        # make sure a game is populated
        elif not promise_game:
            promise_game = True
            data.advance_to_next_game()

        rotate = data.should_rotate_to_next_game()
        if data.schedule.games_live() and not rotate:
            data.refresh_game()

        endtime = time.time()
        time_delta = endtime - starttime
        rotate_rate = data.config.rotate_rate_for_status(data.current_game.status())

        if time_delta >= rotate_rate and data.scrolling_finished:
            starttime = time.time()
            if rotate:
                data.advance_to_next_game()


def __render_main(matrix, data):
    MainRenderer(matrix, data).render()


if __name__ == "__main__":
    # Check for led configuration arguments
    command_line_args = args()
    matrixOptions = led_matrix_options(command_line_args)

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
