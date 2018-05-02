from data.status import Status
from renderers.teams import TeamsRenderer
from rgbmatrix import graphics
from utils import get_font, center_text_position
import ledcolors.scoreboard

# "Manager Challenge is too long"
CHALLENGE_SHORTHAND = "Challenge"

# Handle statuses that are too long for 32-wide boards.
POSTPONED_SHORTHAND = 'Postpd'
CANCELLED_SHORTHAND = "Cancl'd"
CHALLENGE_SHORTHAND_32 = "Chalnge"

class StatusRenderer:
  def __init__(self, canvas, scoreboard, data):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.data = data
    self.text_color = graphics.Color(*ledcolors.scoreboard.text)

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.data).render()
    self.__render_game_status()

  def __render_game_status(self):
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = self.__get_text_for_status()
    coords = self.data.config.layout.coords("status_text")
    font = self.data.config.layout.font("status_text")
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], text_x, coords["y"], color, text)

  def __get_text_for_status(self):
    text = self.scoreboard.game_status
    short_text = self.data.config.layout.coords("status_text")["short_text"]
    if short_text:
      return self.__get_short_text(text)
    if text == Status.MANAGER_CHALLENGE:
      return CHALLENGE_SHORTHAND
    if text == Status.DELAYED_START:
      return Status.DELAYED
    return text

  def __get_short_text(self, text):
    if text == Status.POSTPONED:
      return POSTPONED_SHORTHAND
    if text == Status.CANCELLED:
      return CANCELLED_SHORTHAND
    if text == Status.MANAGER_CHALLENGE:
      return CHALLENGE_SHORTHAND_32
    return text
