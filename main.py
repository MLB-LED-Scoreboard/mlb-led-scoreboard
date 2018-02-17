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

now = datetime.datetime.now()
year = now.year
month = now.month
day = now.day

if args.standings:
  standings = mlbgame.standings(datetime.datetime(year, month, day))
  division = next(division for division in standings.divisions if division.name == args.standings)
  renderers.standings.render(matrix, canvas, division)
else:
  while True:
    games = mlbgame.games(year, month, day)
    if not len(games):
      renderers.offday.render(matrix, canvas)
    else:
      renderers.games.render(matrix, canvas, games[0], args)
