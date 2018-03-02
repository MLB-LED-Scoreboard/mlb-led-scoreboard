from renderers.games import GameRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.scoreboard_config import ScoreboardConfig
import renderers.standings
import renderers.offday
import datetime
import mlbgame
import debug

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)
canvas = matrix.CreateFrameCanvas()

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config.json")
debug.set_debug_status(config)

# Render the current standings or today's games depending on
# the provided arguments
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day

if config.display_standings:
  standings = mlbgame.standings(datetime.datetime(year, month, day))
  division = next(division for division in standings.divisions if division.name == config.preferred_division)
  renderers.standings.render(matrix, matrix.CreateFrameCanvas(), division)
else:
  while True:
    games = mlbgame.day(year, month, day)
    if not len(games):
      renderers.offday.render(matrix, matrix.CreateFrameCanvas())
    else:
      GameRenderer(matrix, matrix.CreateFrameCanvas(), games, config).render()
