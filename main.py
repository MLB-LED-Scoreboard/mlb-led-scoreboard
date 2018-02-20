from renderers.games import GameRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options, ScoreboardConfig
import renderers.standings
import renderers.offday
import datetime
import mlbgame

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)
canvas = matrix.CreateFrameCanvas()

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config.json")

# Render the current standings or today's games depending on
# the provided arguments
now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day

if config.display_standings:
  standings = mlbgame.standings(datetime.datetime(year, month, day))
  division = next(division for division in standings.divisions if division.name == config.preferred_division)
  renderers.standings.render(matrix, canvas, division)
else:
  while True:
    games = mlbgame.games(year, month, day)
    if not len(games):
      renderers.offday.render(matrix, canvas)
    else:
      # The mlbgame API returns a 2D array with the list of games as the first index,
      # hence the 'games[0]'
      GameRenderer(matrix, canvas, games[0], args, config).render()
