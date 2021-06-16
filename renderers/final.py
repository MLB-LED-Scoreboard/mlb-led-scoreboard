try:
  from rgbmatrix import graphics
except ImportError:
  from RGBMatrixEmulator import graphics
  
from utils import get_font, center_text_position
from renderers.teams import TeamsRenderer
from renderers.scrollingtext import ScrollingText
from renderers.nohitter import NoHitterRenderer
from renderers.network import NetworkErrorRenderer
import data.layout

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
    NetworkErrorRenderer(self.canvas, self.data).render()
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

    if self.data.config.layout.state_is_nohitter():
      nohit_text = NoHitterRenderer(self.canvas, self.data).nohitter_text()
      nohit_coords = self.data.config.layout.coords("final.nohit_text")
      nohit_color = self.colors.graphics_color("final.nohit_text")
      nohit_font = self.data.config.layout.font("final.nohit_text")
      graphics.DrawText(self.canvas, nohit_font["font"], nohit_coords["x"], nohit_coords["y"], nohit_color, nohit_text)
