from rgbmatrix import graphics
from utils import get_font, center_text_position
from renderers.teams import TeamsRenderer
import ledcolors.scoreboard

NORMAL_GAME_LENGTH = 9

class Final:
  def __init__(self, canvas, game, scoreboard, config, scroll_pos):
    self.canvas = canvas
    self.font = get_font()
    self.game = game
    self.scoreboard = scoreboard
    self.config = config
    self.text_color = graphics.Color(*ledcolors.scoreboard.text)
    self.scroll_pos = scroll_pos

  def render(self):
    TeamsRenderer(self.canvas, self.scoreboard.home_team, self.scoreboard.away_team, self.config).render()
    self.__render_final_inning()
    return self.__render_scroll_text()

  def __render_scroll_text(self):
    scroll_text = "W: %s %s-%s L: %s %s-%s" % (
      self.game.winning_pitcher, self.game.winning_pitcher_wins, self.game.winning_pitcher_losses,
      self.game.losing_pitcher, self.game.losing_pitcher_wins, self.game.losing_pitcher_losses)
    return graphics.DrawText(self.canvas, self.font, self.scroll_pos, self.config.coords["final"]["pitchers"]["y"], self.text_color, scroll_text)

  def __render_final_inning(self):
    color = graphics.Color(*ledcolors.scoreboard.text)
    text = "FINAL"
    if self.scoreboard.inning.number != NORMAL_GAME_LENGTH:
      text += " " + str(self.scoreboard.inning.number)
    text_x = center_text_position(text, self.canvas.width)
    graphics.DrawText(self.canvas, self.font, text_x, self.config.coords["final"]["inning"]["y"], color, text)
