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

def display_standings(matrix, config, date):
  standings = mlbgame.standings(date)
  division = next(division for division in standings.divisions if division.name == config.preferred_division)
  renderers.standings.render(matrix, matrix.CreateFrameCanvas(), division)

if config.display_standings:
	display_standings(matrix, config, datetime.datetime(year, month, day))
else:
  while True:
    games = mlbgame.day(year, month, day)
    if not len(games):
      if config.display_standings_on_offday:
        try:
          display_standings(matrix, config, datetime.datetime(year, month, day))
        except:
          # Out of season off days don't always return standings so fall back on the offday renderer
          renderers.offday.render(matrix, matrix.CreateFrameCanvas())
      else:
        renderers.offday.render(matrix, matrix.CreateFrameCanvas())
    else:
      GameRenderer(matrix, matrix.CreateFrameCanvas(), games, config).render()
