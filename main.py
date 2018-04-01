from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderers.games import GameRenderer
from renderers.offday import OffdayRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
import renderers.standings
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
config = ScoreboardConfig("config.json", matrix.width, matrix.height)
debug.set_debug_status(config)

# Render the current standings or today's games depending on
# the provided arguments
today = datetime.today()
end_of_day = datetime.strptime(config.end_of_day, "%H:%M").replace(year=today.year, month=today.month, day=today.day)
if end_of_day > datetime.now():
  today -= timedelta(days=1)
year = today.year
month = today.month
day = today.day

def display_standings(matrix, config, date):
  standings = mlbgame.standings(date)
  division = next(division for division in standings.divisions if division.name == config.preferred_division)
  renderers.standings.render(matrix, matrix.CreateFrameCanvas(), division, config.coords["standings"])

if config.display_standings:
	display_standings(matrix, config, datetime(year, month, day))
else:
  while True:
    games = mlbgame.day(year, month, day)
    if not len(games):
      if config.display_standings_on_offday:
        try:
          display_standings(matrix, config, datetime(year, month, day))
        except:
          # Out of season off days don't always return standings so fall back on the offday renderer
          OffdayRenderer(matrix, matrix.CreateFrameCanvas(), datetime(year, month, day)).render()
      else:
        OffdayRenderer(matrix, matrix.CreateFrameCanvas(), datetime(year, month, day)).render()
    else:
      GameRenderer(matrix, matrix.CreateFrameCanvas(), games, config).render()
