from rgbmatrix import RGBMatrix
from utils import args
from renderer import render_games, render_standings
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
  # TODO: Uncomment once the season starts, testing with random games for now
  # games = mlbgame.games(year, month, day)[0]
  games = mlbgame.games(2017, 9, 30)[0]
  render_games(matrix, canvas, games, args)
