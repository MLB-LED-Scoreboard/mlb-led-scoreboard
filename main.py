import debug
from data.data import Data
from data.scoreboard_config import ScoreboardConfig
from renderers.main import MainRenderer
from utils import args, led_matrix_options

try:
    from rgbmatrix import RGBMatrix, version

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

    # Print some basic info on startup
    debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

    # Read scoreboard options from config.json if it exists
    config = ScoreboardConfig("config", matrix.width, matrix.height)
    debug.set_debug_status(config)

    if emulated:
        debug.log("rgbmatrix not installed, falling back to emulator!")
        debug.log("Using RGBMatrixEmulator version {}".format(version.__version__))
    else:
        debug.log("Using rgbmatrix version {}".format(version.__version__))

    # Create a new data object to manage the MLB data
    # This will fetch initial data from MLB
    data = Data(config)

    MainRenderer(matrix, data).render()


if __name__ == "__main__":
    main(args())
