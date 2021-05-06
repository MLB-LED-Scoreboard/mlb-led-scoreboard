from data.status import Status
from renderers.teams import TeamsRenderer
from renderers.scrollingtext import ScrollingText
from renderers.network import NetworkErrorRenderer
from rgbmatrix import graphics
from utils import get_font, center_text_position

# "Manager Challenge is too long"
CHALLENGE_SHORTHAND = "Challenge"

# Handle statuses that are too long for 32-wide boards.
POSTPONED_SHORTHAND = 'Postpd'
CANCELLED_SHORTHAND = "Cancl'd"
SUSPENDED_SHORTHAND = "Suspnd"
CHALLENGE_SHORTHAND_32 = "Chalnge"
UMPIRE_REVIEW_SHORTHAND = "Review"

class StatusRenderer:
  def __init__(self, canvas, scoreboard, data, scroll_pos = 0, status_scroll_pos = 0):
    self.canvas = canvas
    self.scoreboard = scoreboard
    self.data = data
    self.colors = data.config.scoreboard_colors
    self.bgcolor = self.colors.graphics_color("default.background")
    self.scroll_pos = scroll_pos
    self.status_scroll_pos = status_scroll_pos

  def render(self):
    if self.scoreboard.get_text_for_reason():
      scrolling_text_len = self.__render_scroll_text()
    else:
      scrolling_text_len = 0

    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.data).render()
    status_text_len = self.__render_game_status()

    NetworkErrorRenderer(self.canvas, self.data).render()
    return (scrolling_text_len, status_text_len)

  def __render_game_status(self):
    color = self.colors.graphics_color("status.text")
    text = self.__get_text_for_status()
    coords = self.data.config.layout.coords("status.text")
    font = self.data.config.layout.font("status.text")
    text_x = center_text_position(text, coords["x"], font["size"]["width"])

    if self.__text_should_scroll(text, font, text_x):
      graphics.DrawText(self.canvas, font["font"], text_x, coords["y"], color, text)
      return 0
    else:
      return ScrollingText(self.canvas, 0, coords["y"], self.canvas.width, font, color, self.bgcolor, text).render(self.status_scroll_pos)

  def __render_scroll_text(self):
    coords = self.data.config.layout.coords("status.scrolling_text")
    font = self.data.config.layout.font("status.scrolling_text")
    color = self.colors.graphics_color("status.scrolling_text")
    scroll_text = "{}".format(self.scoreboard.get_text_for_reason())
    return ScrollingText(self.canvas, coords["x"], coords["y"], coords["width"], font, color, self.bgcolor, scroll_text).render(self.scroll_pos)

  def __get_text_for_status(self):
    text = self.scoreboard.game_status
    short_text = self.data.config.layout.coords("status.text")["short_text"]
    if short_text:
      return self.__get_short_text(text)
    if text == Status.MANAGER_CHALLENGE:
      return CHALLENGE_SHORTHAND
    if text == Status.DELAYED_START:
      return Status.DELAYED
    return text

  def __get_short_text(self, text):
    if "delayed" in text.lower():
      return Status.DELAYED
    if "postponed" in text.lower():
      return POSTPONED_SHORTHAND
    if "cancelled" in text.lower():
      return CANCELLED_SHORTHAND
    if "challenge" in text.lower():
      return CHALLENGE_SHORTHAND_32
    if "review" in text.lower():
      return UMPIRE_REVIEW_SHORTHAND
    if "suspended" in text.lower():
      return SUSPENDED_SHORTHAND
    return text

  def __text_should_scroll(self, text, font, x_offset):
    return len(text) * font["size"]["width"] + x_offset <= self.canvas.width
