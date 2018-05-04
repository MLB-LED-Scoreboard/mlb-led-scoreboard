from rgbmatrix import graphics
from utils import get_font, center_text_position
from renderers.teams import TeamsRenderer
from renderers.scrollingtext import ScrollingText
import ledcolors.scoreboard

NORMAL_GAME_LENGTH = 9

class Final:
  def __init__(self, canvas, game, scoreboard, data, scroll_pos):
    self.canvas = canvas
    self.game = game
    self.scoreboard = scoreboard
    self.data = data
    self.colors = data.config.scoreboard_colors
    self.bgcolor = self.colors.graphics_color("default.background")
    self.scroll_pos = scroll_pos

  def render(self):
    text_len = self.__render_scroll_text()
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.data).render()
    self.__render_final_inning()
    return text_len

  def __render_scroll_text(self):
    coords = self.data.config.layout.coords("final.scrolling_text")
    font = self.data.config.layout.font("final.scrolling_text")
    color = self.colors.graphics_color("final.scrolling_text")
    scroll_text = "W: {} {}-{} L: {} {}-{}".format(
      self.game.winning_pitcher, self.game.winning_pitcher_wins, self.game.winning_pitcher_losses,
      self.game.losing_pitcher, self.game.losing_pitcher_wins, self.game.losing_pitcher_losses)
    if self.game.save_pitcher:
      scroll_text += " SV: {} ({})".format(self.game.save_pitcher, self.game.save_pitcher_saves)
    return ScrollingText(self.canvas, coords["x"], coords["y"], coords["width"], font, color, self.bgcolor, scroll_text).render(self.scroll_pos)

  def __render_final_inning(self):
    text = "FINAL"
    color = self.colors.graphics_color("final.inning")
    coords = self.data.config.layout.coords("final.inning")
    font = self.data.config.layout.font("final.inning")
    if self.scoreboard.inning.number != NORMAL_GAME_LENGTH:
      text += " " + str(self.scoreboard.inning.number)
    text_x = center_text_position(text, coords["x"], font["size"]["width"])
    graphics.DrawText(self.canvas, font["font"], text_x, coords["y"], color, text)
