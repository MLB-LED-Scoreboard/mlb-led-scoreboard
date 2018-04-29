from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderers.main import MainRenderer
from renderers.offday import OffdayRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.data import Data
import renderers.standings
import mlbgame
import debug

SCRIPT_NAME = "MLB LED Scoreboard"
SCRIPT_VERSION = "1.4.0.SNAPSHOT"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config.json", matrix.width, matrix.height)
debug.set_debug_status(config)

# Create a new data object to manage the MLB data
# This will fetch initial data from MLB
data = Data(config)

# Print some basic info on startup
debug.info("{} - v{}".format(SCRIPT_NAME, SCRIPT_VERSION))

# Render the standings or an off day screen
def display_standings(matrix, data):
  try:
    division = data.standings_for_preferred_division()
    renderers.standings.render(matrix, matrix.CreateFrameCanvas(), division, config.coords["standings"])
  except:
    # Out of season off days don't always return standings so fall back on the offday renderer
    OffdayRenderer(matrix, matrix.CreateFrameCanvas(), datetime(data.year, data.month, data.day)).render()

# Check if we should just display the standings
if config.display_standings:
	display_standings(matrix, data)

# Otherwise, we'll start displaying games depending on config settings
else:
  # No baseball today.
  if data.is_offday():
    if config.display_standings_on_offday:
      display_standings(matrix, data)
    else:
      OffdayRenderer(matrix, matrix.CreateFrameCanvas(), datetime(data.year, data.month, data.day)).render()

  # Baseball!
  else:
    if config.preferred_team:
      if data.is_offday_for_preferred_team() and config.display_standings_on_offday == 2:
        display_standings(matrix, data)
      else:
        MainRenderer(matrix, data).render()
