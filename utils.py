from scoreboard import Scoreboard
from scoreboard_renderer import ScoreboardRenderer
import argparse

def refresh_scoreboard(canvas, game):
  scoreboard = Scoreboard(game)
  if not scoreboard.game_data:
    return False
  renderer = ScoreboardRenderer(canvas, scoreboard)
  renderer.render()
  return True

def bump_counter(counter, arr, rotate):
  counter += 1
  if counter >= len(arr) and rotate:
    counter = 0
  return counter

def args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-t', '--team', help='Pick a team to display a game for. Example: "Cubs"')
  parser.add_argument(
      '-r', '--rotate', help='Rotate through each game of the day every 15 seconds', action='store_true')
  parser.add_argument(
      '-s', '--standings', help='Display standings for the provided division. Example: "NL Central"', metavar="division")
  return parser.parse_args()
