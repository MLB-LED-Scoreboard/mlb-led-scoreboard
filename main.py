from rgbmatrix import RGBMatrix
from utils import args
from renderer import render_games, render_standings, render_offday
import datetime
import mlbgame

# Initialize the matrix and fill it in with a dark blue color
matrix = RGBMatrix()
canvas = matrix.CreateFrameCanvas()
args = args()

if args.standings:
  standings = mlbgame.standings(datetime.datetime(2017, 9, 30))
  division = next(division for division in standings.divisions if division.name == args.standings)
  render_standings(matrix, canvas, division)
else:
  now = datetime.datetime.now()
  year = now.year
  month = now.month
  day = now.day
  # TODO: Uncomment once the season starts, testing with random games for now
  # Uncomment now if you want to see the offday/offseason message
  # games = mlbgame.games(year, month, day)
  games = mlbgame.games(2017, 9, 30)
  if not len(games):
    render_offday(matrix, canvas)
  else:
    render_games(matrix, canvas, games[0], args)
