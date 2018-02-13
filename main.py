from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
import renderers.games
import renderers.standings
import renderers.offday
import datetime
import mlbgame

args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix and fill it in with a dark blue color
matrix = RGBMatrix(options = matrixOptions)
canvas = matrix.CreateFrameCanvas()

if args.standings:
  # TODO: Uncomment once the season starts, testing with random days for now
  # standings = mlbgame.standings(datetime.datetime(year, month, day))
  standings = mlbgame.standings(datetime.datetime(2017, 9, 30))
  division = next(division for division in standings.divisions if division.name == args.standings)
  renderers.standings.render(matrix, canvas, division)
else:
  now = datetime.datetime.now()
  year = now.year
  month = now.month
  day = now.day

  while True:
    # TODO: Uncomment once the season starts, testing with random games for now
    # Uncomment now if you want to see the offday/offseason message
    # games = mlbgame.games(year, month, day)
    games = mlbgame.games(2018, 2, 23)
    if not len(games):
      renderers.offday.render(matrix, canvas)
    else:
      renderers.games.render(matrix, canvas, games[0], args)
