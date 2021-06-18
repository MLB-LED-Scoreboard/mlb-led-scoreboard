from data.scoreboard_config import ScoreboardConfig
from renderers.main import MainRenderer

try:
    from rgbmatrix import RGBMatrix
except ImportError:
    from RGBMatrixEmulator import RGBMatrix

import debug
from data.data import Data
from utils import args, led_matrix_options

SCRIPT_NAME = "MLB LED Scoreboard"
SCRIPT_VERSION = "4.0.1"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options=matrixOptions)

# Print some basic info on startup
debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", matrix.width, matrix.height)
debug.set_debug_status(config)

# Create a new data object to manage the MLB data
# This will fetch initial data from MLB
data = Data(config)

MainRenderer(matrix, data).render()
