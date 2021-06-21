import logging

import debug
from data.config import Config
from data.data import Data
from renderers.main import MainRenderer
from utils import args, led_matrix_options

try:
    from rgbmatrix import RGBMatrix, __version__

    emulated = False
except ImportError:
    from RGBMatrixEmulator import RGBMatrix, version

    emulated = True


SCRIPT_NAME = "MLB LED Scoreboard"
SCRIPT_VERSION = "5.0.0-dev"


def main(args_in):
    # Check for led configuration arguments
    matrixOptions = led_matrix_options(args_in)

    # Initialize the matrix
    matrix = RGBMatrix(options=matrixOptions)

    # Read scoreboard options from config.json if it exists
    config = Config("config", matrix.width, matrix.height)
    logger = logging.getLogger("mlbled")
    if config.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    # Print some basic info on startup
    debug.info("%s - v%s (%sx%s)", SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height)

    if emulated:
        debug.log("rgbmatrix not installed, falling back to emulator!")
        debug.log("Using RGBMatrixEmulator version %s", version.__version__)
    else:
        debug.log("Using rgbmatrix version %s", __version__)

    # Create a new data object to manage the MLB data
    # This will fetch initial data from MLB
    data = Data(config)

    MainRenderer(matrix, data).render()


if __name__ == "__main__":
    main(args())
