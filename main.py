import sys

from bullpen.logging import LOGGER

if sys.version_info < (3, 10):
    LOGGER.error("Please run with Python >= 3.10")
    sys.exit(1)

import statsapi

statsapi_version = tuple(map(int, statsapi.__version__.split(".")))
if statsapi_version < (1, 9, 0):
    LOGGER.error("We require MLB-StatsAPI 1.9.0 or higher. You may need to re-run install.sh")
    sys.exit(1)

import os
import threading
import time

from PIL import Image
from pathlib import Path

import driver
from utils import setup_logger


from data import Data
from data.config import Config
from data.plugins import load_plugins

from renderers.main import MainRenderer
from version import SCRIPT_NAME, SCRIPT_VERSION


def main(matrix, config):
    # Set the scoreboard logger
    setup_logger(config.debug)

    # Print some basic info on startup
    LOGGER.info("%s - v%s (%sx%s)", SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height)

    if driver.is_emulated():
        if driver.hardware_load_failed:
            LOGGER.debug("rgbmatrix not installed, falling back to emulator!")

        LOGGER.debug("Using RGBMatrixEmulator version %s", __version__)
    else:
        LOGGER.debug("Using rgbmatrix version %s", __version__)

    # Draw startup screen
    logo_filename = "mlb-w{}h{}.png".format(matrix.width, matrix.height)
    logo_path = (Path(__file__).parent / "assets" / logo_filename).resolve()

    # MLB image disabled when using renderer, for now.
    # see: https://github.com/ty-porter/RGBMatrixEmulator/issues/9#issuecomment-922869679
    if os.path.exists(logo_path) and driver.is_hardware():
        logo = Image.open(logo_path)
        matrix.SetImage(logo.convert("RGB"))
        logo.close()

    plugins = load_plugins(config)

    plugin_data = {name: data for name, (data, _) in plugins.items()}

    # Create a new data object to manage the MLB data
    # This will fetch initial data from MLB
    data = Data(config, plugin_data)

    # create render thread
    plugin_renderers = {name: renderer for name, (_, renderer) in plugins.items()}
    render = threading.Thread(
        target=__render_main, args=[matrix, data, plugin_renderers], name="render_thread", daemon=True
    )
    time.sleep(1)
    render.start()

    while render.is_alive():
        time.sleep(0.1)
        data.refresh_schedule()
        time.sleep(0.1)
        if data.schedule.num_games():
            data.refresh_game()
        time.sleep(0.1)
        for plugin in plugin_data:
            if data.config.screen_time_at_priority(plugin, data.schedule.priority):
                data.refresh_plugin(plugin)
        time.sleep(0.2)


def __render_main(matrix, data, plugins):
    MainRenderer(matrix, data, plugins).render()


if __name__ == "__main__":
    config = Config()

    if config.emulated:
        driver.set_mode(driver.DriverMode.SOFTWARE_EMULATION)

    if driver.is_emulated():
        config.matrix_options.emulator_title = f"{SCRIPT_NAME} v{SCRIPT_VERSION}"
        config.matrix_options.icon_path = (Path(__file__).parent / "assets" / "mlb-emulator-icon.png").resolve()

    from driver import RGBMatrix, __version__

    matrix = RGBMatrix(options=config.matrix_options)

    try:
        main(matrix, config)
    except:
        LOGGER.exception("Untrapped error in main!")
        sys.exit(1)
    finally:
        matrix.Clear()
