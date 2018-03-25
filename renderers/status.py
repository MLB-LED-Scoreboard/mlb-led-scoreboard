from renderers.teams import TeamsRenderer
from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard

# "Postponed" is too long a word for 32-wide displays,
# so we use a shorthand for that case.
POSTPONED = 'Postponed'
POSTPONED_SHORTHAND = 'Postpd'

CANCELLED = 'Cancelled'
CANCELLED_SHORTHAND = "Cancl'd"

class Status:
  def __init__(self, canvas, scoreboard, coords):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.coords = coords
    self.font = get_font()
    self.text_color = graphics.Color(*ledcolors.scoreboard.text)

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.coords["teams"]).render()
    self.__render_game_status()

  def __render_game_status(self):
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = self.scoreboard.game_status
    if self.canvas.width == 32:
      if text == POSTPONED:
        text = POSTPONED_SHORTHAND
      if text == CANCELLED:
        text = CANCELLED_SHORTHAND
    text_x = center_text_position(text, self.canvas.width)
    graphics.DrawText(self.canvas, self.font, text_x, self.coords["status"]["y"], color, text)
